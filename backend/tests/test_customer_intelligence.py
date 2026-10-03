import pytest
from datetime import datetime, timedelta, UTC
import uuid

from app.core.database import SessionLocal
from app.models.customer import Customer, Account, CustomerProfile, CustomerSegment
from app.models.transaction import Transaction
from app.services.customer_intelligence import CustomerProfileService, CustomerBehaviorService, CustomerLifecycleService, CustomerSegmentationService, Customer360Service

def setup_customer(db, num_old_tx, num_new_tx, old_amount=100.0, new_amount=100.0):
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    
    acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db.add(acc)
    db.commit()
    
    now = datetime.now(UTC)
    
    # Old txs (15 days ago)
    for _ in range(num_old_tx):
        tx = Transaction(
            amount=old_amount, currency="USD", transaction_type="SEND", 
            sender_account_id=acc.id, status="RECEIVED", 
            idempotency_key=str(uuid.uuid4()), created_at=now - timedelta(days=15)
        )
        db.add(tx)
        
    # New txs (2 days ago)
    for _ in range(num_new_tx):
        tx = Transaction(
            amount=new_amount, currency="USD", transaction_type="SEND", 
            sender_account_id=acc.id, status="RECEIVED", 
            idempotency_key=str(uuid.uuid4()), created_at=now - timedelta(days=2)
        )
        db.add(tx)
        
    db.commit()
    
    # Run profile update
    for tx in db.query(Transaction).filter_by(sender_account_id=acc.id).all():
        CustomerProfileService.process_transaction(db, tx)
        
    return cust.id

def test_customer_segmentation_high_activity():
    db = SessionLocal()
    cust_id = setup_customer(db, 15, 10) # 25 txs total
    
    seg = db.query(CustomerSegment).filter_by(customer_id=cust_id).first()
    assert seg.segment_name == "HIGH_ACTIVITY"
    db.close()

def test_customer_lifecycle_dormant():
    db = SessionLocal()
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    
    prof = CustomerProfile(customer_id=cust.id, transaction_count=5, last_activity_at=datetime.now(UTC) - timedelta(days=100))
    db.add(prof)
    db.commit()
    
    CustomerLifecycleService.evaluate(db, prof)
    assert prof.lifecycle_state == "DORMANT"
    db.close()

def test_customer_behavior_change():
    db = SessionLocal()
    # 5 old txs of $100, 5 new txs of $1000
    cust_id = setup_customer(db, 5, 5, 100.0, 1000.0)
    
    signals = CustomerBehaviorService.evaluate(db, cust_id)
    assert len(signals) == 1
    assert signals[0].signal_type == "CUSTOMER_BEHAVIOR_CHANGE"
    
    prof = db.query(CustomerProfile).filter_by(customer_id=cust_id).first()
    assert prof.behavioral_stability == "HIGHLY_CHANGING"
    
    db.close()

def test_customer_360_api_data():
    db = SessionLocal()
    cust_id = setup_customer(db, 1, 1) # 2 txs total
    
    data = Customer360Service.get_profile(db, cust_id)
    assert data["customer_id"] == cust_id
    assert data["profile"]["transaction_count"] == 2
    assert data["segment"]["segment_name"] == "LOW_ACTIVITY"
    db.close()
