import pytest
from datetime import datetime, timedelta, UTC
import uuid

from app.core.database import SessionLocal
from app.models.customer import Customer, Account
from app.models.transaction import Transaction, Merchant, MerchantProfile, Agent, AgentProfile
from app.services.merchant_intelligence import MerchantProfileService, MerchantBehaviorService
from app.services.agent_intelligence import AgentProfileService, AgentBehaviorService

def setup_merchant_env(db, num_old_tx, num_new_tx, old_amount=100.0, new_amount=100.0):
    merchant = Merchant(name="Test Merchant", category="RETAIL")
    db.add(merchant)
    
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    
    acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db.add(acc)
    db.commit()
    
    now = datetime.now(UTC)
    
    for _ in range(num_old_tx):
        tx = Transaction(
            amount=old_amount, currency="USD", transaction_type="PAYMENT", 
            sender_account_id=acc.id, merchant_id=merchant.id, status="COMPLETED", 
            idempotency_key=str(uuid.uuid4()), created_at=now - timedelta(days=15)
        )
        db.add(tx)
        
    for _ in range(num_new_tx):
        tx = Transaction(
            amount=new_amount, currency="USD", transaction_type="PAYMENT", 
            sender_account_id=acc.id, merchant_id=merchant.id, status="COMPLETED", 
            idempotency_key=str(uuid.uuid4()), created_at=now - timedelta(days=2)
        )
        db.add(tx)
        
    db.commit()
    
    for tx in db.query(Transaction).filter_by(merchant_id=merchant.id).all():
        MerchantProfileService.process_transaction(db, tx)
        
    return merchant.id

def test_merchant_profile_metrics():
    db = SessionLocal()
    m_id = setup_merchant_env(db, 2, 2, 50.0, 50.0) # 4 txs, total 200
    
    prof = db.query(MerchantProfile).filter_by(merchant_id=m_id).first()
    assert prof.transaction_count == 4
    assert prof.transaction_volume == 200.0
    assert prof.unique_customer_count == 1
    assert prof.successful_transaction_count == 4
    db.close()

def test_merchant_behavior_spike():
    db = SessionLocal()
    m_id = setup_merchant_env(db, 5, 5, 100.0, 1000.0) # Big spike in recent 5
    
    signals = MerchantBehaviorService.evaluate(db, m_id)
    assert any(s.signal_type == "MERCHANT_VOLUME_SPIKE" for s in signals)
    db.close()

def setup_agent_env(db, num_old_tx, num_new_tx, old_amount=100.0, new_amount=100.0):
    agent = Agent(identifier=str(uuid.uuid4()))
    db.add(agent)
    
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    
    acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db.add(acc)
    db.commit()
    
    now = datetime.now(UTC)
    
    for _ in range(num_old_tx):
        tx = Transaction(
            amount=old_amount, currency="USD", transaction_type="DEPOSIT", 
            sender_account_id=acc.id, agent_id=agent.id, status="COMPLETED", 
            idempotency_key=str(uuid.uuid4()), created_at=now - timedelta(days=15)
        )
        db.add(tx)
        
    for _ in range(num_new_tx):
        tx = Transaction(
            amount=new_amount, currency="USD", transaction_type="DEPOSIT", 
            sender_account_id=acc.id, agent_id=agent.id, status="COMPLETED", 
            idempotency_key=str(uuid.uuid4()), created_at=now - timedelta(days=2)
        )
        db.add(tx)
        
    db.commit()
    
    for tx in db.query(Transaction).filter_by(agent_id=agent.id).all():
        AgentProfileService.process_transaction(db, tx)
        
    return agent.id

def test_agent_behavior_spike():
    db = SessionLocal()
    a_id = setup_agent_env(db, 5, 5, 100.0, 1000.0) # Big spike
    
    signals = AgentBehaviorService.evaluate(db, a_id)
    assert any(s.signal_type == "AGENT_VOLUME_SPIKE" for s in signals)
    db.close()
