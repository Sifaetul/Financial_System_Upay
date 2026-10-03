import pytest
import uuid
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.investigation import Alert, InvestigationCase, CaseNote
from app.services.alert_engine import AlertEngine
from app.services.investigation_service import InvestigationService
from app.schemas.risk import RiskEvaluationResult, RiskEvaluationSignalSchema
from app.models.identity import User
from app.core.security import get_password_hash

def setup_user(db: Session):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"investigator_{user_id}@nexus.com",
        password_hash=get_password_hash("password123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    return user_id

def test_alert_generation_and_deduplication(monkeypatch):
    db = SessionLocal()
    tx_id = str(uuid.uuid4())
    
    class DummyTx:
        id = tx_id
        sender_account_id = "sender_123"
        receiver_account_id = "receiver_123"
        device_id = "device_123"
        location_id = "loc_123"
    
    original_query = db.query
    def mock_query(*args, **kwargs):
        if len(args) > 0 and hasattr(args[0], "__name__") and args[0].__name__ == "Transaction":
            class MockQuery:
                def filter_by(self, **fkwargs):
                    class MockResult:
                        def first(self):
                            return DummyTx()
                    return MockResult()
            return MockQuery()
        return original_query(*args, **kwargs)

    monkeypatch.setattr(db, "query", mock_query)

    decision = RiskEvaluationResult(
        transaction_id=tx_id, event_id=tx_id,
        score=95.0,
        category="CRITICAL",
        decision="BLOCK",
        policy_version='1', engine_version='1', confidence_summary=1.0, explanation='Ex', correlation_id='123', causation_id='123', created_at=datetime.now(UTC), id='abc', signals=[RiskEvaluationSignalSchema(id='1', signal_id='1', contribution=1.0,signal_type="ATO_DETECTED", source="FraudIntelligence", raw_value='1.0', explanation='IP mismatch', normalized_value=1.0, weight=1.0, confidence=1.0, reliability=1.0, evidence="IP mismatch", provenance={})]
    )

    # First alert
    alert1 = AlertEngine.generate_alert(db, decision)
    assert alert1 is not None
    assert alert1.severity == "CRITICAL"
    assert alert1.alert_type == "ACCOUNT_TAKEOVER_RISK"
    assert alert1.correlation_group_id is not None
    
    # Second identical alert (should be deduplicated)
    alert2 = AlertEngine.generate_alert(db, decision)
    assert alert2.id == alert1.id

def test_investigation_case_lifecycle():
    db = SessionLocal()
    user_id = setup_user(db)
    tx_id = str(uuid.uuid4())

    alert = Alert(
        alert_type="FRAUD_RISK", severity="CRITICAL", priority=1,
        entity_type="TRANSACTION", entity_id=tx_id, status="NEW",
        deduplication_key=str(uuid.uuid4()), risk_score=85.0
    )
    db.add(alert)
    db.commit()
    
    case = InvestigationService.create_case_from_alert(db, alert)
    assert case is not None
    assert case.status == "OPEN"
    
    InvestigationService.add_note(db, case.id, user_id, "Checking suspicious activity")
    
    db.refresh(case)
    assert len(case.notes) == 1
    
    updated_case = InvestigationService.resolve_case(db, case.id, user_id, "TRUE_POSITIVE", "Confirmed fraud")
    assert updated_case.status == "RESOLVED"
    assert updated_case.resolution_type == "TRUE_POSITIVE"
