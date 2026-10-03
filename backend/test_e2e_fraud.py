from app.core.database import SessionLocal
from app.models.customer import Customer, Account
from app.models.transaction import Transaction
from app.services.fraud_intelligence import FraudContext, FraudFeatureExtractor, FraudIntelligenceOrchestrator
from app.services.risk_engine import UnifiedRiskEngine
import uuid
import json

db = SessionLocal()

# Setup test records
cust = Customer(identifier=str(uuid.uuid4()))
db.add(cust)
db.commit()
db.refresh(cust)

acc1 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
acc2 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
db.add_all([acc1, acc2])
db.commit()
db.refresh(acc1)
db.refresh(acc2)

# Normal tx
tx1 = Transaction(amount=100.0, currency="USD", transaction_type="SEND_MONEY", sender_account_id=acc1.id, receiver_account_id=acc2.id, channel="WEB", status="RECEIVED", idempotency_key=str(uuid.uuid4()))
db.add(tx1)
db.commit()

# Anomalous tx (High amount + Diff Channel)
tx2 = Transaction(amount=5000.0, currency="USD", transaction_type="SEND_MONEY", sender_account_id=acc1.id, receiver_account_id=acc2.id, channel="MOBILE", status="RECEIVED", idempotency_key=str(uuid.uuid4()))
db.add(tx2)
db.commit()

print("Evaluating TX2 Risk")
signals = FraudIntelligenceOrchestrator.evaluate(db, tx2.id, "corr-123")
print("Generated Fraud Signals:")
for s in signals:
    print(f" - {s.signal_type}: {s.normalized_value} ({s.explanation})")

from app.schemas.risk import RiskContext
from datetime import datetime, UTC
context = RiskContext(
    transaction_id=tx2.id,
    amount=5000.0,
    currency="USD",
    transaction_type="SEND_MONEY",
    channel="MOBILE",
    timestamp=datetime.now(UTC),
    correlation_id="corr-123"
)

engine = UnifiedRiskEngine(db)
res = engine.evaluate(context, signals)
print(f"Risk Score: {res.score}")
print(f"Risk Category: {res.category}")
print(f"Risk Decision: {res.decision}")
