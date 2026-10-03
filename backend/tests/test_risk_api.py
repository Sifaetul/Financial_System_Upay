import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.customer import Customer, Account
from app.models.transaction import Transaction
from app.models.identity import User, Role
import uuid

client = TestClient(app)

@pytest.fixture
def get_auth_token():
    email = f"risk_{uuid.uuid4()}@example.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    res = client.post("/api/v1/auth/login", data={"username": email, "password": "StrongPassword123!"})
    token = res.json()["access_token"]
    
    db = SessionLocal()
    u = db.query(User).filter_by(email=email).first()
    
    # Create or update role
    admin_role = db.query(Role).filter_by(name="risk_admin").first()
    if not admin_role:
        admin_role = Role(name="risk_admin", permissions={"keys": ["manage_transactions"]})
        db.add(admin_role)
    else:
        admin_role.permissions = {"keys": ["manage_transactions"]}
    
    if u:
        u.roles.append(admin_role)
        db.commit()
    db.close()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def setup_transaction():
    db = SessionLocal()
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    db.refresh(cust)
    
    acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db.add(acc)
    db.commit()
    db.refresh(acc)
    
    tx = Transaction(amount=15000.0, currency="USD", transaction_type="SEND_MONEY", sender_account_id=acc.id, receiver_account_id=acc.id, status="RECEIVED", idempotency_key=str(uuid.uuid4()))
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    tx_id = tx.id
    db.close()
    return tx_id

def test_evaluate_risk_endpoint(get_auth_token, setup_transaction):
    headers = get_auth_token
    payload = {
        "transaction_id": setup_transaction,
        "amount": 15000.0,
        "currency": "USD",
        "transaction_type": "SEND_MONEY",
        "channel": "API_UNKNOWN"
    }
    
    res = client.post("/api/v1/risk/evaluate", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["transaction_id"] == setup_transaction
    assert data["category"] in ["CRITICAL", "HIGH"]
    assert len(data["signals"]) >= 0
    
    evaluation_id = data["id"]
    
    # Test GET endpoint
    res2 = client.get(f"/api/v1/risk/{evaluation_id}", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["id"] == evaluation_id

def test_evaluate_risk_unauthorized(setup_transaction):
    payload = {
        "transaction_id": setup_transaction,
        "amount": 100.0,
        "currency": "USD",
        "transaction_type": "SEND_MONEY"
    }
    res = client.post("/api/v1/risk/evaluate", json=payload)
    assert res.status_code == 401
