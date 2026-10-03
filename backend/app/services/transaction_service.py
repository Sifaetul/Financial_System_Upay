from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.transaction import Transaction, TransactionEvent
from app.models.event import OutboxEvent
from app.schemas.transaction import TransactionCreate
from fastapi import HTTPException
import uuid
import datetime

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def process_transaction(self, tx_in: TransactionCreate, idempotency_key: str, correlation_id: str = None) -> Transaction:
        # Check idempotency quickly in memory (read)
        if idempotency_key:
            existing_tx = self.db.query(Transaction).filter(Transaction.idempotency_key == idempotency_key).first()
            if existing_tx:
                # Same payload? Simplification: we just return the existing if it exists
                return existing_tx
                
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # State 1: RECEIVED
        new_tx = Transaction(
            amount=tx_in.amount,
            currency=tx_in.currency,
            transaction_type=tx_in.transaction_type,
            sender_account_id=tx_in.sender_account_id,
            receiver_account_id=tx_in.receiver_account_id,
            external_transaction_id=tx_in.external_transaction_id,
            channel=tx_in.channel,
            status="RECEIVED",
            idempotency_key=idempotency_key,
            correlation_id=correlation_id
        )
        
        new_tx.id = str(uuid.uuid4())
        self.db.add(new_tx)
        
        # Outbox Event
        outbox = OutboxEvent(
            event_type="transaction.received",
            schema_version=1,
            aggregate_type="Transaction",
            aggregate_id=new_tx.id, # Needs to be resolved after flush if autoincrement, but we use uuid default so it exists
            correlation_id=correlation_id,
            causation_id=None,
            payload={"status": "RECEIVED", "amount": tx_in.amount}
        )
        self.db.add(outbox)

        try:
            self.db.commit()
            self.db.refresh(new_tx)
        except IntegrityError as e:
            self.db.rollback()
            # If it's a unique violation on idempotency_key due to concurrent insert
            if "ix_transactions_idempotency_key" in str(e):
                existing_tx = self.db.query(Transaction).filter(Transaction.idempotency_key == idempotency_key).first()
                if existing_tx:
                    return existing_tx
            print(f'INTEGRITY ERROR: {e}'); raise HTTPException(status_code=409, detail=f"Idempotency conflict or Invalid Reference: {e}")
            
        return new_tx

    def advance_status(self, transaction_id: str, new_status: str, event_payload: dict = None) -> Transaction:
        tx = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        valid_transitions = {
            "RECEIVED": ["VALIDATED", "FAILED"],
            "VALIDATED": ["PROCESSING", "FAILED"],
            "PROCESSING": ["COMPLETED", "FAILED"],
            "COMPLETED": ["REVERSED"],
            "FAILED": []
        }
        
        if new_status not in valid_transitions.get(tx.status, []):
            raise HTTPException(status_code=400, detail=f"Invalid state transition from {tx.status} to {new_status}")
            
        tx.status = new_status
        
        outbox = OutboxEvent(
            event_type=f"transaction.{new_status.lower()}",
            schema_version=1,
            aggregate_type="Transaction",
            aggregate_id=tx.id,
            correlation_id=tx.correlation_id,
            payload=event_payload or {"status": new_status}
        )
        self.db.add(outbox)
        self.db.commit()
        self.db.refresh(tx)
        return tx
