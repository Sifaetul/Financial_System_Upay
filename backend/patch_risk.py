import re

with open("app/services/risk_engine.py", "r") as f:
    content = f.read()

if "MonitoringService.log_metric" not in content:
    content = content.replace(
        "from typing import List, Dict",
        "from typing import List, Dict\nfrom .monitoring_service import MonitoringService\nimport time"
    )
    
    orig = "def evaluate_transaction(db: Session, transaction: Transaction) -> RiskEvaluation:"
    new = """def evaluate_transaction(db: Session, transaction: Transaction) -> RiskEvaluation:
        start_t = time.time()
"""
    content = content.replace(orig, new)

    orig2 = "return evaluation"
    new2 = """        
        latency_ms = (time.time() - start_t) * 1000
        MonitoringService.log_metric(db, "risk_evaluation_latency_ms", "HISTOGRAM", latency_ms, "unified_risk_engine")
        MonitoringService.log_metric(db, "risk_evaluations_total", "COUNTER", 1.0, "unified_risk_engine")
        MonitoringService.log_metric(db, f"risk_decision_{evaluation.decision}", "COUNTER", 1.0, "unified_risk_engine")
        
        return evaluation
"""
    content = content.replace(orig2, new2)

with open("app/services/risk_engine.py", "w") as f:
    f.write(content)
