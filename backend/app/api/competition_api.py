from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from typing import Dict, Any

from app.core.database import get_db
from app.services.competition_service import CompetitionService
from app.schemas.risk import RiskContext
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/competition", tags=["competition"])

@router.get("/evolution/{entity_id}")
def get_risk_evolution(entity_id: str, entity_type: str = "CUSTOMER", db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    res = CompetitionService.calculate_risk_evolution(db, entity_id, entity_type)
    return {"entity_id": res.entity_id, "risk_score": res.risk_score, "delta_1h": res.delta_1h}

@router.post("/fraud-ring/{entity_id}")
def detect_fraud_ring(entity_id: str, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    signal = CompetitionService.detect_fraud_ring(db, entity_id)
    if not signal:
        return {"status": "No ring detected"}
    return {"signal_type": signal.signal_type}

@router.post("/replay/{evaluation_id}")
def replay_decision(evaluation_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    res = CompetitionService.replay_decision(db, evaluation_id)
    return {"replayed_score": res.replayed_score, "divergence": res.divergence}

@router.post("/simulate/what-if")
def simulate_what_if(context: RiskContext, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    res = CompetitionService.simulate_what_if(db, context, [])
    return {"results": res.results}

@router.post("/simulate/scenario")
def simulate_scenario(scenario_name: str, parameters: Dict[str, Any], db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN"]))):
    res = CompetitionService.simulate_scenario(db, scenario_name, parameters)
    return {"name": res.name}

@router.post("/fusion/{entity_id}")
def fuse_intelligence(entity_id: str, context_data: Dict[str, Any], db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    res = CompetitionService.fuse_intelligence(db, entity_id, context_data)
    return {"entity_id": res.entity_id, "aggregated_context": res.aggregated_context}

@router.post("/threats/{entity_id}")
def detect_threats(entity_id: str, entity_type: str = "CUSTOMER", db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    signal = CompetitionService.detect_proactive_threats(db, entity_id, entity_type)
    if not signal:
        return {"status": "No threats detected"}
    return {"signal_type": signal.signal_type}

@router.post("/feedback")
def add_feedback(target_id: str, target_type: str, feedback_type: str, comments: str, db: Session = Depends(get_db), user=Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    res = CompetitionService.add_feedback(db, target_id, target_type, feedback_type, comments, user.id)
    return {"feedback_type": res.feedback_type, "comments": res.comments}
