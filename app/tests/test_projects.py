from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import Project, User
from app.core.security import create_access_token

client = TestClient(app)

def test_create_project():
    # Создание тестового пользователя
    user = User(email="test@example.com", username="testuser", hashed_password="testpass")
    
    # Получение JWT токена
    token = create_access_token(user.id)
    
    response = client.post(
        "/projects/",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
