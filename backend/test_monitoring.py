import sys
import os
import uuid
import datetime
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.database import SessionLocal
from app.models.transaction import Transaction
from app.services.risk_engine import evaluate_transaction
from app.services.monitoring_service import MonitoringService
from app.models.monitoring import MonitoringMetric

db = SessionLocal()

# 1. Trigger Risk Evaluation
tx = Transaction(
    id=str(uuid.uuid4()),
    source_account_id="ACC_MON_1",
    destination_account_id="ACC_MON_2",
    amount=500,
    currency="BDT",
    timestamp=datetime.datetime.now(datetime.UTC),
    status="PENDING",
    channel="WEB"
)
db.add(tx)
db.commit()

evaluate_transaction(db, tx)

# 2. Check Metrics
metrics = db.query(MonitoringMetric).all()
print(f"Total metrics found: {len(metrics)}")
for m in metrics:
    print(f"Metric: {m.name}={m.value} ({m.metric_type}) [Service: {m.service}]")

# 3. Check Dashboard
dashboard = MonitoringService.get_dashboard_summary(db)
print("Dashboard Health:", dashboard["health"]["status"])
print("Active Alerts:", len(dashboard["active_alerts"]))

# 4. Trigger Data Quality Check
dq = MonitoringService.run_data_quality_check(db)
print(f"DQ Feature: {dq.feature}, Status: {dq.status}, Null Rate: {dq.null_rate}")

