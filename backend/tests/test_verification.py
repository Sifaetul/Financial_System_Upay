import pytest
import uuid
from app.core.database import SessionLocal
from app.models.customer import Customer, Account
from app.services.transaction_service import TransactionService
from fastapi import HTTPException
from app.schemas.transaction import TransactionCreate

def test_invalid_state_transition():
    db = SessionLocal()
    service = TransactionService(db)
    
    # Create customer and account
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    db.refresh(cust)
    
    acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db.add(acc)
    db.commit()
    db.refresh(acc)
    
    # Create tx
    tx_in = TransactionCreate(
        amount=100.0,
        currency="USD",
        transaction_type="SEND_MONEY",
        sender_account_id=acc.id,
        receiver_account_id=acc.id
    )
    
    tx = service.process_transaction(tx_in, idempotency_key=str(uuid.uuid4()))
    
    # Valid transition RECEIVED -> VALIDATED
    tx = service.advance_status(tx.id, "VALIDATED")
    assert tx.status == "VALIDATED"
    
    # Invalid transition COMPLETED -> PROCESSING
    with pytest.raises(HTTPException) as excinfo:
        service.advance_status(tx.id, "COMPLETED")
    assert excinfo.value.status_code == 400
    # Wait, VALIDATED -> COMPLETED is invalid!
    with pytest.raises(HTTPException) as excinfo:
        service.advance_status(tx.id, "COMPLETED")
    assert excinfo.value.status_code == 400
    assert "Invalid state transition" in excinfo.value.detail

    db.close()
