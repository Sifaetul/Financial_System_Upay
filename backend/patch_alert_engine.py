with open("app/services/alert_engine.py", "r") as f:
    content = f.read()

content = content.replace("from app.schemas.risk import RiskDecision", "from app.schemas.risk import RiskEvaluationResult\nfrom app.schemas.fraud import FraudSignal")
content = content.replace("RiskDecision", "RiskEvaluationResult")
content = content.replace("decision.risk_category", "decision.category")
content = content.replace("decision.risk_score", "decision.score")

with open("app/services/alert_engine.py", "w") as f:
    f.write(content)
