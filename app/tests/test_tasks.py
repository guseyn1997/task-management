def test_priority_validation(client):
    response = client.post(
        "/tasks/",
        json={"title": "Test", "priority": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422
    assert "value is not a valid enumeration member" in response.text
