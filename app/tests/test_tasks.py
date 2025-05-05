def test_priority_validation(client):
    user = User(email="test@example.com", username="testuser", hashed_password="testpass")
    token = create_access_token(user.id)
    
    response = client.post(
        "/tasks/",
        json={"title": "Test", "priority": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422
