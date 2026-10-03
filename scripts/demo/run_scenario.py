import argparse
import sys
import uuid
import time
import requests
import os

# Add backend to path to import models if needed, though requests are better
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.core.database import SessionLocal
from app.models.customer import Customer, Account
from app.models.transaction import Transaction

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    email = f"demo_admin_{uuid.uuid4()}@example.com"
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    
    # We need to manually assign ADMIN role in DB because register doesn't
    db = SessionLocal()
    from app.models.identity import User, Role
    user = db.query(User).filter(User.email == email).first()
    admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
    if not admin_role:
        admin_role = Role(name="ADMIN", permissions={"keys": ["*"]})
        db.add(admin_role)
    user.roles.append(admin_role)
    db.commit()
    db.close()

    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": "StrongPassword123!"})
    return res.json()["access_token"]

def generate_synthetic_data(db, scenario):
    # Base setup
    c1 = Customer(identifier=f"demo_sender_{uuid.uuid4()}")
    c2 = Customer(identifier=f"demo_receiver_{uuid.uuid4()}")
    db.add_all([c1, c2])
    db.commit()

    a1 = Account(customer_id=c1.id, balance=10000.0, account_number_hash=str(uuid.uuid4()))
    a2 = Account(customer_id=c2.id, balance=500.0, account_number_hash=str(uuid.uuid4()))
    db.add_all([a1, a2])
    db.commit()

    return a1.id, a2.id

def submit_transaction(token, payload):
    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": str(uuid.uuid4())}
    res = requests.post(f"{BASE_URL}/transactions", json=payload, headers=headers)
    print(f"Transaction Submit: {res.status_code}")
    print(res.json())
    return res.json()

def run_normal_transaction(token, db):
    print("Running Normal Transaction Scenario...")
    s_acc, r_acc = generate_synthetic_data(db, "normal")
    submit_transaction(token, {
        "amount": 50.0,
        "currency": "USD",
        "transaction_type": "SEND_MONEY",
        "sender_account_id": str(s_acc),
        "receiver_account_id": str(r_acc),
        "device_id": "normal_device_1",
        "location_id": "normal_location_1"
    })

def run_fraud_ring(token, db):
    print("Running Fraud Ring Scenario...")
    s_acc1, r_acc = generate_synthetic_data(db, "fraud_ring_1")
    s_acc2, _ = generate_synthetic_data(db, "fraud_ring_2")
    s_acc3, _ = generate_synthetic_data(db, "fraud_ring_3")

    # Shared device fraud ring fan-in
    shared_device = "suspicious_shared_device_X"

    submit_transaction(token, {
        "amount": 900.0,
        "currency": "USD",
        "transaction_type": "SEND_MONEY",
        "sender_account_id": str(s_acc1),
        "receiver_account_id": str(r_acc),
        "device_id": shared_device
    })
    submit_transaction(token, {
        "amount": 950.0,
        "currency": "USD",
        "transaction_type": "SEND_MONEY",
        "sender_account_id": str(s_acc2),
        "receiver_account_id": str(r_acc),
        "device_id": shared_device
    })
    submit_transaction(token, {
        "amount": 980.0,
        "currency": "USD",
        "transaction_type": "SEND_MONEY",
        "sender_account_id": str(s_acc3),
        "receiver_account_id": str(r_acc),
        "device_id": shared_device
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UPAY NEXUS AI Demo Scenario Runner")
    parser.add_argument("--scenario", choices=["normal_transaction", "fraud_ring"], required=True)
    args = parser.parse_args()

    db = SessionLocal()
    token = get_admin_token()

    if args.scenario == "normal_transaction":
        run_normal_transaction(token, db)
    elif args.scenario == "fraud_ring":
        run_fraud_ring(token, db)

    print("Scenario execution complete.")
