import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.database import SessionLocal
from app.models.transaction import Transaction
from app.services.risk_engine import UnifiedRiskEngine
from app.schemas.risk import RiskContext
from app.services.monitoring_service import MonitoringService
from app.models.monitoring import MonitoringMetric, ModelLineage
from sqlalchemy import func

def verify_all():
    db = SessionLocal()

    # Initial check
    initial_metrics_count = db.query(func.count(MonitoringMetric.id)).scalar()

    print(f"INITIAL: METRICS={initial_metrics_count}")

    # Process transactions
    tx = db.query(Transaction).first()
    if tx:
        context = RiskContext(transaction_id=tx.id, event_id="evt", correlation_id="corr", causation_id="cause", amount=tx.amount, currency=tx.currency, channel="WEB", transaction_type="TRANSFER", timestamp=__import__("datetime").datetime.now(__import__("datetime").UTC))
        engine = UnifiedRiskEngine(db)
        engine.evaluate(context, [])

    # Post processing check
    final_metrics_count = db.query(func.count(MonitoringMetric.id)).scalar()

    print(f"FINAL: METRICS={final_metrics_count}")
    print(f"METRICS INCREASED: {final_metrics_count > initial_metrics_count}")

    # Check metric types
    types = db.query(MonitoringMetric.metric_type).distinct().all()
    print("METRIC TYPES PRESENT:", [t[0] for t in types])

    # Check Health
    health = MonitoringService.get_health(db)
    print("HEALTH STATUS:", health["status"])

    # Lineage check
    lineage = db.query(func.count(ModelLineage.id)).scalar()
    print("MODEL LINEAGE RECORDS:", lineage)

if __name__ == "__main__":
    verify_all()
