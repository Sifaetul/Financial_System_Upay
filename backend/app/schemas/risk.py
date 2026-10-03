from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime

class RiskSignalInput(BaseModel):
    signal_id: str
    signal_type: str
    source: str
    raw_value: Any
    normalized_value: float # 0.0 to 1.0
    weight: float
    confidence: float # 0.0 to 1.0
    reliability: float # 0.0 to 1.0
    explanation: str
    provenance: dict

class RiskContext(BaseModel):
    transaction_id: Optional[str] = None
    event_id: Optional[str] = None
    amount: float
    currency: str
    transaction_type: str
    customer_id: Optional[str] = None
    account_id: Optional[str] = None
    merchant_id: Optional[str] = None
    agent_id: Optional[str] = None
    channel: Optional[str] = None
    timestamp: datetime
    correlation_id: str
    causation_id: Optional[str] = None
    metadata: dict = {}

class RiskEvaluationSignalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    signal_id: str
    signal_type: str
    source: str
    raw_value: Optional[str]
    normalized_value: float
    weight: float
    confidence: float
    reliability: float
    contribution: float
    explanation: str
    provenance: dict

class RiskEvaluationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    transaction_id: Optional[str]
    event_id: Optional[str]
    score: float
    category: str
    decision: str
    policy_version: str
    engine_version: str
    confidence_summary: float
    explanation: str
    correlation_id: str
    causation_id: Optional[str]
    signals: List[RiskEvaluationSignalSchema]
    created_at: datetime
