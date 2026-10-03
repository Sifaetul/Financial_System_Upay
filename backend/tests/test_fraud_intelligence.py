import pytest
from app.core.database import SessionLocal
from app.models.customer import Customer, Account
from app.models.transaction import Transaction
from app.models.intelligence import Rule, RuleVersion
from app.services.fraud_intelligence import (
    FraudContext, FraudFeatureExtractor, VelocityProvider,
    BehavioralProvider, ATOProvider, MuleProvider, RuleProvider
)
import uuid
from datetime import datetime, UTC

def test_fraud_feature_extraction():
    db = SessionLocal()
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    db.refresh(cust)
    
    acc1 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    acc2 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db.add_all([acc1, acc2])
    db.commit()
    
    tx1 = Transaction(amount=100.0, currency="USD", transaction_type="SEND_MONEY", sender_account_id=acc1.id, receiver_account_id=acc2.id, channel="WEB", status="RECEIVED", idempotency_key=str(uuid.uuid4()))
    tx2 = Transaction(amount=150.0, currency="USD", transaction_type="SEND_MONEY", sender_account_id=acc1.id, receiver_account_id=acc2.id, channel="WEB", status="RECEIVED", idempotency_key=str(uuid.uuid4()))
    
    db.add_all([tx1, tx2])
    db.commit()
    db.refresh(tx1)
    db.refresh(tx2)
    
    context = FraudContext(db, tx2.id)
    features = FraudFeatureExtractor.extract(context)
    
    assert features["amount"] == 150.0
    assert features["count_15m"] == 1 # tx1 is the only past tx
    assert features["median_amount_24h"] == 100.0
    
    db.close()

def test_velocity_provider():
    features = {"count_15m": 6}
    signals = VelocityProvider.evaluate(None, features)
    assert len(signals) == 1
    assert signals[0].signal_type == "HIGH_TRANSACTION_VELOCITY"

def test_behavioral_provider():
    features = {"amount": 400.0, "median_amount_24h": 100.0}
    
    class MockContext:
        recent_transactions = []
    
    signals = BehavioralProvider.evaluate(MockContext(), features)

    assert len(signals) == 1
    assert signals[0].signal_type == "AMOUNT_ANOMALY"
    
def test_ato_provider():
    features = {"channel": "MOBILE", "amount": 1000.0, "median_amount_24h": 200.0, "count_15m": 4}
    
    class MockContext:
        recent_transactions = [type('obj', (object,), {"channel": "WEB"})()]
        
    signals = ATOProvider.evaluate(MockContext(), features)
    assert len(signals) == 1
    assert signals[0].signal_type == "ACCOUNT_TAKEOVER_INDICATOR"
    
def test_mule_provider():
    features = {"unique_beneficiaries_24h": 6, "amount_1h": 6000.0}
    signals = MuleProvider.evaluate(None, features)
    assert len(signals) == 1
    assert signals[0].signal_type == "MULE_ACCOUNT_INDICATOR"

def test_rule_provider():
    db = SessionLocal()
    rule = Rule(name=f"test_rule_{uuid.uuid4()}")
    db.add(rule)
    db.flush()
    rv = RuleVersion(rule_id=rule.id, configuration={"type": "threshold", "feature": "amount", "operator": ">", "value": 500.0}, is_active=True)
    db.add(rv)
    db.commit()
    
    features_above = {"amount": 600.0}
    signals = RuleProvider.evaluate(db, None, features_above)
    assert any(s.signal_type == f"RULE_{rule.name.upper()}" for s in signals)
    
    features_below = {"amount": 400.0}
    signals_below = RuleProvider.evaluate(db, None, features_below)
    assert not any(s.signal_type == f"RULE_{rule.name.upper()}" for s in signals_below)
    
    db.close()
