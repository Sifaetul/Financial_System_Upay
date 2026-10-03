import pytest
from datetime import datetime, timedelta, UTC
import uuid

from app.core.database import SessionLocal
from app.models.customer import Customer, Account, FinancialProfile
from app.models.transaction import Transaction
from app.services.financial_intelligence import FinancialProfileService, FinancialBehaviorService

def create_customer_env(db):
    cust = Customer(identifier=str(uuid.uuid4()))
    ext_cust = Customer(identifier=str(uuid.uuid4()))
    db.add_all([cust, ext_cust])
    db.commit()
    
    acc1 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    acc2 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    ext_acc = Account(customer_id=ext_cust.id, account_number_hash=str(uuid.uuid4()))
    
    db.add_all([acc1, acc2, ext_acc])
    db.commit()
    return cust.id, acc1.id, acc2.id, ext_acc.id

def test_internal_transfer_exclusion():
    db = SessionLocal()
    c_id, a1_id, a2_id, ext_id = create_customer_env(db)
    
    tx = Transaction(
        amount=500.0, currency="USD", transaction_type="SEND", 
        sender_account_id=a1_id, receiver_account_id=a2_id, status="RECEIVED", 
        idempotency_key=str(uuid.uuid4()), created_at=datetime.now(UTC)
    )
    db.add(tx)
    db.commit()
    
    FinancialProfileService.process_transaction(db, tx)
    prof = db.query(FinancialProfile).filter_by(customer_id=c_id).first()
    
    # Internal transfer should exclude from total inflow and outflow
    assert prof.total_inflow == 0.0
    assert prof.total_outflow == 0.0
    
    db.close()

def test_financial_cash_flow():
    db = SessionLocal()
    c_id, a1_id, a2_id, ext_id = create_customer_env(db)
    
    tx_in = Transaction(
        amount=2000.0, currency="USD", transaction_type="SEND", 
        sender_account_id=ext_id, receiver_account_id=a1_id, status="RECEIVED", 
        idempotency_key=str(uuid.uuid4()), created_at=datetime.now(UTC) - timedelta(days=10)
    )
    tx_out = Transaction(
        amount=500.0, currency="USD", transaction_type="SEND", 
        sender_account_id=a1_id, receiver_account_id=ext_id, status="RECEIVED", 
        idempotency_key=str(uuid.uuid4()), created_at=datetime.now(UTC) - timedelta(days=1)
    )
    db.add_all([tx_in, tx_out])
    db.commit()
    
    FinancialProfileService.process_transaction(db, tx_in)
    FinancialProfileService.process_transaction(db, tx_out)
    
    prof = db.query(FinancialProfile).filter_by(customer_id=c_id).first()
    assert prof.total_inflow == 2000.0
    assert prof.total_outflow == 500.0
    assert prof.net_cash_flow == 1500.0
    assert prof.financial_health_score == "STABLE"
    assert prof.data_sufficiency == "SUFFICIENT_DATA"
    
    db.close()

def test_financial_stress_signal():
    db = SessionLocal()
    c_id, a1_id, a2_id, ext_id = create_customer_env(db)
    
    tx_in = Transaction(
        amount=100.0, currency="USD", transaction_type="SEND", 
        sender_account_id=ext_id, receiver_account_id=a1_id, status="RECEIVED", 
        idempotency_key=str(uuid.uuid4()), created_at=datetime.now(UTC) - timedelta(days=10)
    )
    tx_out = Transaction(
        amount=5000.0, currency="USD", transaction_type="SEND", 
        sender_account_id=a1_id, receiver_account_id=ext_id, status="RECEIVED", 
        idempotency_key=str(uuid.uuid4()), created_at=datetime.now(UTC) - timedelta(days=1)
    )
    db.add_all([tx_in, tx_out])
    db.commit()
    
    FinancialProfileService.process_transaction(db, tx_out) # Triggers update evaluating all past txs
    
    prof = db.query(FinancialProfile).filter_by(customer_id=c_id).first()
    assert prof.net_cash_flow == -4900.0
    assert prof.financial_health_score == "PRESSURED"
    
    signals = FinancialBehaviorService.evaluate(db, c_id)
    assert any(s.signal_type == "NEGATIVE_NET_CASH_FLOW" for s in signals)
    
    db.close()
