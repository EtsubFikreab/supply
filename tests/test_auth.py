def test_signup(client):
    response = client.post("/signup", data={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["message"] == "Signup successful. Please check your email to verify your account."

def test_login(client):
    response = client.post("/login", data={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
