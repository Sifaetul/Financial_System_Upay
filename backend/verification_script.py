import requests
import uuid
import time
from app.core.database import SessionLocal
from app.models.event import OutboxEvent, ProcessedEvent, DeadLetterEvent
from app.models.transaction import Transaction

base_url = "http://localhost:8000/api/v1"
email = f"verif_{uuid.uuid4()}@example.com"
password = "StrongPassword123!"

# Register
requests.post(f"{base_url}/auth/register", json={
    "email": email, "password": password, "password_confirm": password
})

# Login
res = requests.post(f"{base_url}/auth/login", data={"username": email, "password": password})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create accounts via db
db = SessionLocal()
from app.models.identity import User
from app.models.customer import Customer, Account
user = db.query(User).filter_by(email=email).first()
cust = Customer(identifier=str(uuid.uuid4()))
db.add(cust)
db.commit()
db.refresh(cust)

acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
db.add(acc)
db.commit()
db.refresh(acc)
db.close()

fake_account_id = acc.id

# 1. State transition test
# Create tx
idem_key = str(uuid.uuid4())
headers["Idempotency-Key"] = idem_key
payload = {
    "amount": 100,
    "currency": "USD",
    "transaction_type": "SEND_MONEY",
    "sender_account_id": fake_account_id,
    "receiver_account_id": fake_account_id
}
res = requests.post(f"{base_url}/transactions", json=payload, headers=headers)
tx_id = res.json()["id"]

print("TX created:", res.status_code)

# Let's try to update status directly? No endpoint exists for `advance_status` unless we use internal service!
# Let me just write tests or use internal service to verify state transition.

