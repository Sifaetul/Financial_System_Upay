from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_permissions
from app.models.intelligence import Rule, RuleVersion
from pydantic import BaseModel
from typing import List

router = APIRouter()

class RuleCreate(BaseModel):
    name: str
    feature: str
    operator: str
    value: float
    normalized_value: float
    weight: float

@router.post("/rules")
def create_rule(
    req: RuleCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    rule = db.query(Rule).filter(Rule.name == req.name).first()
    if not rule:
        rule = Rule(name=req.name)
        db.add(rule)
        db.flush()
    
    rv = RuleVersion(
        rule_id=rule.id,
        configuration={
            "type": "threshold",
            "feature": req.feature,
            "operator": req.operator,
            "value": req.value,
            "normalized_value": req.normalized_value,
            "weight": req.weight
        },
        is_active=True
    )
    db.add(rv)
    db.commit()
    return {"status": "success", "rule_id": rule.id}

@router.get("/rules")
def list_rules(
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    rules = db.query(Rule).all()
    out = []
    for r in rules:
        active_version = next((v for v in r.versions if v.is_active), None)
        if active_version:
            out.append({
                "id": r.id,
                "name": r.name,
                "configuration": active_version.configuration
            })
    return out
