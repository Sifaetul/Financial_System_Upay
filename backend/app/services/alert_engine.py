from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import List, Optional
import uuid
import json

from app.models.investigation import Alert, AlertHistory, AlertCorrelationGroup
from app.schemas.fraud import FraudSignal
from app.schemas.risk import RiskEvaluationResult
from app.schemas.fraud import FraudSignal

class AlertEngine:
    @staticmethod
    def generate_alert(db: Session, decision: RiskEvaluationResult) -> Optional[Alert]:
        if decision.category not in ["HIGH", "CRITICAL"]:
            return None
            
        # Deduplication
        dedup_key = f"{decision.transaction_id}_{decision.category}_{datetime.now(UTC).strftime('%Y-%m-%d-%H')}"
        existing = db.query(Alert).filter_by(deduplication_key=dedup_key).first()
        
        if existing:
            return existing
            
        alert_type = "FRAUD_RISK"
        if any(s.signal_type.startswith("MERCHANT") for s in decision.signals):
            alert_type = "MERCHANT_RISK"
        elif any(s.signal_type.startswith("AGENT") for s in decision.signals):
            alert_type = "AGENT_RISK"
        elif any(s.signal_type == "ATO_DETECTED" for s in decision.signals):
            alert_type = "ACCOUNT_TAKEOVER_RISK"
            
        alert = Alert(
            alert_type=alert_type,
            severity=decision.category,
            priority=1 if decision.category == "CRITICAL" else 0,
            entity_type="TRANSACTION",
            entity_id=decision.transaction_id,
            status="NEW",
            deduplication_key=dedup_key,
            risk_score=decision.score,
            trigger_reason=f"Risk Score {decision.score:.2f} ({decision.category})"
        )
        
        db.add(alert)
        db.flush()
        
        history = AlertHistory(
            alert_id=alert.id,
            new_status="NEW",
            reason="Alert Generated",
            metadata_json={"risk_score": decision.score}
        )
        db.add(history)
        
        # Correlate
        AlertEngine._correlate_alert(db, alert)
        
        db.flush()
        return alert

    @staticmethod
    def _correlate_alert(db: Session, alert: Alert):
        from app.models.transaction import Transaction
        tx = db.query(Transaction).filter_by(id=alert.entity_id).first()
        if not tx:
            return
            
        # Simple correlation: same sender account in recent timeframe
        recent_group = db.query(AlertCorrelationGroup).filter_by(
            primary_entity_type="ACCOUNT",
            primary_entity_id=tx.sender_account_id,
            status="OPEN"
        ).first()
        
        if not recent_group:
            recent_group = AlertCorrelationGroup(
                group_key=f"ACCT_{tx.sender_account_id}_{uuid.uuid4().hex[:8]}",
                primary_entity_type="ACCOUNT",
                primary_entity_id=tx.sender_account_id,
                correlation_reason="Common Account"
            )
            db.add(recent_group)
            db.flush()
            
        alert.correlation_group_id = recent_group.id
        
    @staticmethod
    def update_status(db: Session, alert_id: str, new_status: str, user_id: str = None, reason: str = None):
        alert = db.query(Alert).filter_by(id=alert_id).first()
        if not alert:
            return None
            
        old_status = alert.status
        alert.status = new_status
        
        history = AlertHistory(
            alert_id=alert.id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=user_id,
            reason=reason
        )
        db.add(history)
        db.flush()
        return alert
