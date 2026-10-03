from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_permissions, get_current_user
from app.models.investigation import Alert, InvestigationCase, CaseEvidence, CaseNote, CaseAction
from app.services.investigation_service import InvestigationService
from app.services.alert_engine import AlertEngine

router = APIRouter()

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db), _ = Depends(require_permissions(["view_alerts"]))):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(100).all()
    return [{"id": a.id, "type": a.alert_type, "severity": a.severity, "priority": a.priority, "status": a.status, "entity_type": a.entity_type, "entity_id": a.entity_id, "created_at": a.created_at} for a in alerts]

@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    alert = AlertEngine.update_status(db, alert_id, "ACKNOWLEDGED", user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "alert_id": alert.id, "new_status": alert.status}

@router.get("/cases")
def get_cases(db: Session = Depends(get_db), _ = Depends(require_permissions(["view_cases"]))):
    cases = db.query(InvestigationCase).order_by(InvestigationCase.created_at.desc()).limit(100).all()
    return [{"id": c.id, "number": c.case_number, "status": c.status, "priority": c.priority, "severity": c.severity, "assigned_investigator_id": c.assigned_investigator_id} for c in cases]

@router.get("/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db), _ = Depends(require_permissions(["view_cases"]))):
    case = db.query(InvestigationCase).filter_by(id=case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    evidence = db.query(CaseEvidence).filter_by(case_id=case.id).all()
    notes = db.query(CaseNote).filter_by(case_id=case.id).all()
    actions = db.query(CaseAction).filter_by(case_id=case.id).order_by(CaseAction.created_at.asc()).all()
    
    return {
        "id": case.id,
        "number": case.case_number,
        "title": case.title,
        "description": case.description,
        "status": case.status,
        "severity": case.severity,
        "entity_id": case.primary_entity_id,
        "assigned_investigator_id": case.assigned_investigator_id,
        "evidence": [{"id": e.id, "type": e.evidence_type, "relevance": e.relevance, "explanation": e.explanation} for e in evidence],
        "notes": [{"id": n.id, "content": n.content, "author_id": n.author_id, "created_at": n.created_at} for n in notes],
        "timeline": [{"id": a.id, "action": a.action_type, "details": a.details, "created_at": a.created_at} for a in actions]
    }

@router.post("/cases/{case_id}/resolve")
def resolve_case(case_id: str, resolution: str, reason: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    case = InvestigationService.resolve_case(db, case_id, user.id, resolution, reason)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"status": "success", "case_id": case.id, "resolution": case.resolution_type}
    
@router.post("/cases/{case_id}/notes")
def add_note(case_id: str, content: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    note = InvestigationService.add_note(db, case_id, user.id, content)
    return {"status": "success", "note_id": note.id}
