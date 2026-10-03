import pytest
from datetime import datetime, UTC
import uuid

from app.core.database import SessionLocal
from app.models.investigation import Alert, InvestigationCase, AlertCorrelationGroup, CaseEvidence
from app.models.identity import User
from app.services.investigation_service import InvestigationService

print("Starting trace...")
db = SessionLocal()
print("SessionLocal created")

user = User(email=f"investigator_{uuid.uuid4()}@upaynexus.com", password_hash="hashed")
db.add(user)
print("User added, committing...")
db.commit()
print("User committed. ID:", user.id)

tx_id = str(uuid.uuid4())
alert = Alert(
    alert_type="FRAUD_RISK", severity="CRITICAL", priority=1,
    entity_type="TRANSACTION", entity_id=tx_id, status="NEW",
    deduplication_key=str(uuid.uuid4()), risk_score=85.0
)
db.add(alert)
print("Alert added, committing...")
db.commit()
print("Alert committed. ID:", alert.id)

case = InvestigationService.create_case_from_alert(db, alert)
print("Case created:", case.id)

evidence = db.query(CaseEvidence).filter_by(case_id=case.id).first()
print("Evidence found:", evidence.id if evidence else None)

note = InvestigationService.add_note(db, case.id, user.id, "Checking transaction history.")
print("Note added:", note.id)

resolved_case = InvestigationService.resolve_case(db, case.id, user.id, "CONFIRMED_RISK", "Fraud confirmed via call")
print("Case resolved:", resolved_case.status)

db.close()
print("Done.")
