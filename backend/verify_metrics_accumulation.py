import sys
import os
import uuid
import time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.database import SessionLocal
from app.models.monitoring import MonitoringMetric, DataQualityResult, GovernanceEvent
from sqlalchemy import func

def test_metrics():
    db = SessionLocal()
    
    pre_metrics = db.query(func.count(MonitoringMetric.id)).scalar()
    pre_dq = db.query(func.count(DataQualityResult.id)).scalar()
    pre_gov = db.query(func.count(GovernanceEvent.id)).scalar()
    
    print(f"PRE-METRICS: {pre_metrics}")
    print(f"PRE-DQ: {pre_dq}")
    print(f"PRE-GOV: {pre_gov}")
    
    # 1. Trigger DQ
    from app.services.monitoring_service import MonitoringService
    dq = MonitoringService.run_data_quality_check(db)
    print(f"Triggered DQ Check: {dq.id} - Status: {dq.status}")
    
    # 2. Trigger Governance
    gov = MonitoringService.log_governance_event(
        db, "admin", "model", "model-v1", "APPROVED", reason="Manual Approval"
    )
    print(f"Triggered GOV Event: {gov.id} - Action: {gov.action}")
    
    # 3. Simulate API Call Metric
    metric = MonitoringService.log_metric(
        db, "api_request", "COUNTER", 1.0, "API", {"endpoint": "/api/v1/health"}
    )
    print(f"Triggered API Metric: {metric.id}")
    
    post_metrics = db.query(func.count(MonitoringMetric.id)).scalar()
    post_dq = db.query(func.count(DataQualityResult.id)).scalar()
    post_gov = db.query(func.count(GovernanceEvent.id)).scalar()
    
    print(f"POST-METRICS: {post_metrics} (Diff: {post_metrics - pre_metrics})")
    print(f"POST-DQ: {post_dq} (Diff: {post_dq - pre_dq})")
    print(f"POST-GOV: {post_gov} (Diff: {post_gov - pre_gov})")
    
    assert post_metrics > pre_metrics
    assert post_dq > pre_dq
    assert post_gov > pre_gov
    print("SUCCESS: Metric accumulation verified dynamically via database.")

if __name__ == "__main__":
    test_metrics()
