import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_register_user():
    response = client.post(
        "/register",
        json={"email": "test@example.com", "username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User successfully registered"}

def test_login_user():
    client.post(
        "/register",
        json={"email": "login@example.com", "username": "loginuser", "password": "loginpassword"},
    )
  
    response = client.post(
        "/token",
        data={"username": "loginuser", "password": "loginpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_protected_endpoint():
    client.post(
        "/register",
        json={"email": "protected@example.com", "username": "protecteduser", "password": "protectedpass"},
    )

    login_response = client.post(
        "/token",
        data={"username": "protecteduser", "password": "protectedpass"},
    )
    access_token = login_response.json()["access_token"]
    
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "protecteduser"
