from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_permissions
from app.models.transaction import Agent, AgentProfile
from typing import List, Dict, Any

router = APIRouter()

@router.get("/{agent_id}/intelligence")
def get_agent_intelligence(
    agent_id: str,
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    agent = db.query(Agent).filter_by(id=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    profile = db.query(AgentProfile).filter_by(agent_id=agent_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Agent profile not found")
        
    from app.services.agent_intelligence import AgentBehaviorService
    signals = AgentBehaviorService.evaluate(db, agent_id)
        
    return {
        "agent_id": agent.id,
        "identifier": agent.identifier,
        "transaction_count": profile.transaction_count,
        "transaction_volume": profile.transaction_volume,
        "unique_customer_count": profile.unique_customer_count,
        "average_transaction_amount": profile.average_transaction_amount,
        "successful_transaction_count": profile.successful_transaction_count,
        "failed_transaction_count": profile.failed_transaction_count,
        "reversal_count": profile.reversal_count,
        "data_sufficiency": profile.data_sufficiency,
        "signals": [s.model_dump() for s in signals]
    }
