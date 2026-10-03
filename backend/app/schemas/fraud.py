from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import datetime

class FraudSignal(BaseModel):
    signal_type: str
    provider: str
    raw_value: Any
    normalized_value: float # 0.0 to 1.0
    weight: float
    confidence: float
    reliability: float
    severity: str
    evidence: str
    explanation: str
    provenance: dict
