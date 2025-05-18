from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app import crud, schemas
from app.core import security
from app.core.config import settings
from app.core.dependencies import get_db

# Rate limiter implementation
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post(
    "/login", 
    response_model=schemas.Token,
    summary="User login",
    description="OAuth2 compatible token login, get an access token for future authentication"
)
@limiter.limit("5/minute")
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    """
    Authenticate user and provide access token for future authentication
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post(
    "/register", 
    response_model=schemas.User,
    summary="Register new user",
    description="Create new user account with email verification"
)
@limiter.limit("3/minute")
def register_new_user(
    user_in: schemas.UserCreate, 
    db: Session = Depends(get_db)
) -> schemas.User:
    """
    Register a new user and send verification email
    """
    # Check if email already exists
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Check if username already exists
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )
    
    # Create user with is_active=False until email is verified
    user_data = user_in.dict()
    user_data["is_active"] = False
    user = crud.user.create(db, obj_in=schemas.UserCreate(**user_data))
    
    # Generate verification token
    verification_token = security.create_email_verification_token(user.email)
    
    # TODO: Implement email sending functionality
    # send_verification_email(user.email, verification_token) 
    
    return user

@router.get(
    "/verify-email/{token}",
    response_model=schemas.Msg,
    summary="Verify user email",
    description="Verify user email using the token sent to their email address"
)
def verify_email(
    token: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Verify user email using token
    """
    email = security.decode_email_verification_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_active:
        return {"msg": "Email already verified"}
    
    # Activate user
    crud.user.update(db, db_obj=user, obj_in={"is_active": True})
    return {"msg": "Email verified successfully"}
