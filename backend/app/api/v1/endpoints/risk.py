from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, require_permissions
from app.models.identity import User
from app.models.risk import RiskEvaluation
from app.schemas.risk import RiskContext, RiskEvaluationResult, RiskSignalInput
from app.services.risk_engine import UnifiedRiskEngine
from app.services.fraud_intelligence import FraudIntelligenceOrchestrator
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, UTC
import uuid

router = APIRouter()

class RiskEvaluationRequest(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    transaction_type: str
    channel: str = "WEB"
    signals: Optional[List[RiskSignalInput]] = None # Optional external signals

@router.post("/evaluate", response_model=RiskEvaluationResult)
def evaluate_risk(
    req: RiskEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["manage_transactions"])) # or a specific risk permission
):
    context = RiskContext(
        transaction_id=req.transaction_id,
        amount=req.amount,
        currency=req.currency,
        transaction_type=req.transaction_type,
        channel=req.channel,
        timestamp=datetime.now(UTC),
        correlation_id=str(uuid.uuid4())
    )
    
    signals = req.signals or []
    
    # If no explicit signals provided, use collector
    if not signals:
        signals = FraudIntelligenceOrchestrator.evaluate(db, req.transaction_id, context.correlation_id)
        
    engine = UnifiedRiskEngine(db)
    evaluation = engine.evaluate(context, signals)
    
    return evaluation

@router.get("/{evaluation_id}", response_model=RiskEvaluationResult)
def get_evaluation(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["manage_transactions"]))
):
    ev = db.query(RiskEvaluation).filter(RiskEvaluation.id == evaluation_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Risk evaluation not found")
    return ev

@router.get("/transaction/{transaction_id}", response_model=List[RiskEvaluationResult])
def get_transaction_evaluations(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["manage_transactions"]))
):
    evs = db.query(RiskEvaluation).filter(RiskEvaluation.transaction_id == transaction_id).order_by(RiskEvaluation.created_at.desc()).all()
    return evs
