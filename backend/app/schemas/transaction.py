from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    transaction_type: str
    sender_account_id: str
    receiver_account_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    channel: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    transaction_type: str
    sender_account_id: str
    receiver_account_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    correlation_id: Optional[str] = None
    channel: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EventEnvelope(BaseModel):
    event_id: str
    event_type: str
    event_version: int
    occurred_at: str
    aggregate_type: str
    aggregate_id: str
    correlation_id: Optional[str]
    causation_id: Optional[str]
    payload: dict
