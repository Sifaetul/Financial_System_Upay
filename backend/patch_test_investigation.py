with open("tests/test_investigation.py", "r") as f:
    content = f.read()

content = content.replace("from app.schemas.risk import RiskDecision", "from app.schemas.risk import RiskEvaluationResult, RiskEvaluationSignalSchema")
content = content.replace("decision = RiskDecision(", "decision = RiskEvaluationResult(")
content = content.replace("risk_category=", "category=")
content = content.replace("risk_score=", "score=")
content = content.replace("signals=[FraudSignal(", "policy_version='1', engine_version='1', confidence_summary=1.0, explanation='Ex', correlation_id='123', causation_id='123', created_at=datetime.now(UTC), id='abc', signals=[RiskEvaluationSignalSchema(id='1', signal_id='1', contribution=1.0,")
content = content.replace("provider=", "source=")

with open("tests/test_investigation.py", "w") as f:
    f.write(content)
