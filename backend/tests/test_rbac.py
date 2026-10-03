import pytest
from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import require_permissions, get_current_user

router = APIRouter()
@router.get("/admin-only", dependencies=[Depends(require_permissions(["admin:all"]))])
def admin_only():
    return {"status": "ok"}
    
app.include_router(router, prefix="/api/v1/test-rbac")

client = TestClient(app)

def test_rbac_denial():
    client.post("/api/v1/auth/register", json={
        "email": "rbac_deny@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    login_res = client.post("/api/v1/auth/login", data={"username": "rbac_deny@example.com", "password": "StrongPassword123!"})
    token = login_res.json()["access_token"]
    
    res = client.get("/api/v1/test-rbac/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.json()["detail"] == "Not enough permissions"
