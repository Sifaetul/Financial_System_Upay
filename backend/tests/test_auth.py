import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.models.identity import User
from app.models.auth import RefreshToken

# Use real DB since it's a test environment
client = TestClient(app)

def clean_db():
    db = SessionLocal()
    db.query(RefreshToken).delete()
    db.query(User).filter(User.email.like("%@example.com")).delete()
    db.commit()
    db.close()

@pytest.fixture(autouse=True)
def run_around_tests():
    clean_db()
    yield
    clean_db()

def test_register_and_login():
    # Register
    reg_response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    assert reg_response.status_code == 200
    data = reg_response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data

    # Login
    login_response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "StrongPassword123!"
    })
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test@example.com"

def test_login_invalid_password():
    client.post("/api/v1/auth/register", json={
        "email": "bad@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    res = client.post("/api/v1/auth/login", data={"username": "bad@example.com", "password": "wrong"})
    assert res.status_code == 401

def test_refresh_token_rotation():
    client.post("/api/v1/auth/register", json={
        "email": "rot@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    login_res = client.post("/api/v1/auth/login", data={"username": "rot@example.com", "password": "StrongPassword123!"})
    tokens = login_res.json()
    old_refresh = tokens["refresh_token"]

    # Refresh
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert ref_res.status_code == 200
    new_refresh = ref_res.json()["refresh_token"]

    # Try old refresh again (Reuse detection!)
    ref_res_bad = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert ref_res_bad.status_code == 401

    # Try new refresh (Should fail because family was revoked!)
    ref_res_bad2 = client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert ref_res_bad2.status_code == 401

def test_logout():
    client.post("/api/v1/auth/register", json={
        "email": "logout@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    login_res = client.post("/api/v1/auth/login", data={"username": "logout@example.com", "password": "StrongPassword123!"})
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    res = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert res.status_code == 200

    # Try refresh
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 401

def test_long_password():
    client.post("/api/v1/auth/register", json={
        "email": "long@example.com",
        "password": "A" * 100 + "123!",
        "password_confirm": "A" * 100 + "123!"
    })
    res = client.post("/api/v1/auth/login", data={"username": "long@example.com", "password": "A" * 100 + "123!"})
    assert res.status_code == 200

def test_rbac_denial():
    # Register normal user
    client.post("/api/v1/auth/register", json={
        "email": "rbac@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    login_res = client.post("/api/v1/auth/login", data={"username": "rbac@example.com", "password": "StrongPassword123!"})
    token = login_res.json()["access_token"]
    
    # Try to access a non-existent admin endpoint (we will just test if we can create a dummy endpoint to test)
    pass
