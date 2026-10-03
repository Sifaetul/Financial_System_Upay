from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import List, Optional

from app.models.investigation import InvestigationCase, Alert, CaseEvidence, CaseNote, CaseAction
from app.models.transaction import Transaction

class InvestigationService:
    @staticmethod
    def create_case_from_alert(db: Session, alert: Alert) -> InvestigationCase:
        case = InvestigationCase(
            case_number=f"CAS-{alert.created_at.strftime('%Y%m%d')}-{alert.id[:6].upper()}",
            title=f"Investigation for {alert.alert_type}",
            description=alert.trigger_reason,
            priority=alert.priority,
            severity=alert.severity,
            primary_entity_type=alert.entity_type,
            primary_entity_id=alert.entity_id
        )
        db.add(case)
        db.flush()
        
        alert.case_id = case.id
        
        # Attach initial evidence
        evidence = CaseEvidence(
            case_id=case.id,
            evidence_type=alert.entity_type,
            source_entity_type=alert.entity_type,
            source_entity_id=alert.entity_id,
            relevance="Primary trigger",
            explanation=alert.trigger_reason
        )
        db.add(evidence)
        db.flush()
        
        return case

    @staticmethod
    def add_note(db: Session, case_id: str, author_id: str, content: str) -> CaseNote:
        note = CaseNote(
            case_id=case_id,
            author_id=author_id,
            content=content
        )
        db.add(note)
        db.flush()
        return note
        
    @staticmethod
    def log_action(db: Session, case_id: str, author_id: str, action_type: str, details: str = None) -> CaseAction:
        action = CaseAction(
            case_id=case_id,
            author_id=author_id,
            action_type=action_type,
            details=details
        )
        db.add(action)
        db.flush()
        return action

    @staticmethod
    def resolve_case(db: Session, case_id: str, author_id: str, resolution: str, reason: str):
        case = db.query(InvestigationCase).filter_by(id=case_id).first()
        if not case:
            return None
            
        case.status = "RESOLVED"
        case.resolution_type = resolution
        case.resolution_reason = reason
        case.resolved_at = datetime.now(UTC)
        
        InvestigationService.log_action(db, case_id, author_id, "RESOLVE_CASE", f"{resolution}: {reason}")
        
        db.flush()
        return case
