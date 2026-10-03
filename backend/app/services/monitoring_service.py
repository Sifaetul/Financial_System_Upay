from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, UTC
from typing import Dict, Any, List
from app.models.monitoring import (
    MonitoringMetric, MonitoringAlert, DataQualityResult, DriftResult, 
    GovernanceEvent, ModelLineage
)
from app.models.transaction import Transaction
from app.models.investigation import InvestigationCase
from app.models.ai import AiChunk

class MonitoringService:
    @staticmethod
    def get_health(db: Session) -> Dict[str, Any]:
        health = {
            "status": "healthy",
            "services": {
                "api": "healthy",
                "database": "healthy",
                "redis": "healthy",
                "ai_provider": "healthy",
                "embedding_provider": "healthy"
            }
        }
        
        # Check DB
        try:
            db.execute(func.now())
        except Exception:
            health["services"]["database"] = "critical"
            health["status"] = "degraded"
            
        # Check embedding provider (pgvector chunks count)
        try:
            db.query(AiChunk).limit(1).all()
        except Exception:
            health["services"]["embedding_provider"] = "critical"
            health["status"] = "degraded"

        return health

    @staticmethod
    def log_metric(db: Session, name: str, metric_type: str, value: float, service: str, dimensions: dict = None) -> MonitoringMetric:
        metric = MonitoringMetric(
            name=name,
            metric_type=metric_type,
            value=value,
            service=service,
            dimensions=dimensions or {}
        )
        db.add(metric)
        db.commit()
        return metric

    @staticmethod
    def log_governance_event(db: Session, actor: str, entity_type: str, entity_id: str, action: str, old_value: dict=None, new_value: dict=None, reason: str=None) -> GovernanceEvent:
        event = GovernanceEvent(
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )
        db.add(event)
        db.commit()
        return event
        
    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        tx_count = db.query(func.count(Transaction.id)).scalar() or 0
        case_count = db.query(func.count(InvestigationCase.id)).scalar() or 0
        
        metrics = db.query(MonitoringMetric).order_by(desc(MonitoringMetric.timestamp)).limit(100).all()
        
        alerts = db.query(MonitoringAlert).filter_by(status="ACTIVE").order_by(desc(MonitoringAlert.timestamp)).limit(50).all()
        
        return {
            "health": MonitoringService.get_health(db),
            "system_metrics": {
                "transactions_processed_total": tx_count,
                "cases_created_total": case_count
            },
            "recent_telemetry": [{"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat()} for m in metrics],
            "active_alerts": [{"condition": a.condition, "severity": a.severity} for a in alerts]
        }

    @staticmethod
    def create_alert(db: Session, condition: str, metric: str, observed_value: float, threshold: float, severity: str, affected_component: str) -> MonitoringAlert:
        alert = MonitoringAlert(
            condition=condition,
            metric=metric,
            observed_value=observed_value,
            threshold=threshold,
            severity=severity,
            affected_component=affected_component
        )
        db.add(alert)
        db.commit()
        return alert

    @staticmethod
    def record_model_lineage(db: Session, model_id: str, model_version: str, prediction: str, correlation_id: str, confidence: float = None) -> ModelLineage:
        lineage = ModelLineage(
            model_id=model_id,
            model_version=model_version,
            prediction=prediction,
            confidence=confidence,
            correlation_id=correlation_id
        )
        db.add(lineage)
        db.commit()
        return lineage

    @staticmethod
    def run_data_quality_check(db: Session) -> DataQualityResult:
        # Example check: transaction amounts
        total = db.query(func.count(Transaction.id)).scalar() or 0
        nulls = db.query(func.count(Transaction.id)).filter(Transaction.amount == None).scalar() or 0
        
        if total == 0:
            status = "HEALTHY"
            null_rate = 0.0
        else:
            null_rate = nulls / total
            status = "HEALTHY" if null_rate < 0.05 else "WARNING"
            
        res = DataQualityResult(
            feature="transaction_amount",
            completeness=1.0 - null_rate,
            null_rate=null_rate,
            invalid_rate=0.0,
            status=status
        )
        db.add(res)
        db.commit()
        return res


    @staticmethod
    def calculate_drift(db: Session, feature: str, baseline_values: List[float], comparison_values: List[float]) -> DriftResult:
        # Simplistic empirical drift: compare means
        if not baseline_values or not comparison_values:
            raise ValueError("Insufficient data")
            
        mean_base = sum(baseline_values) / len(baseline_values)
        mean_comp = sum(comparison_values) / len(comparison_values)
        
        diff = abs(mean_comp - mean_base)
        threshold = 0.5 * (mean_base if mean_base > 0 else 1.0)
        
        is_drift = diff > threshold
        
        res = DriftResult(
            feature=feature,
            baseline_window="baseline_100",
            comparison_window="current_100",
            method="mean_shift",
            metric_value=diff,
            threshold=threshold,
            severity="HIGH" if is_drift else "INFO"
        )
        db.add(res)
        db.commit()
        return res
        
    @staticmethod
    def create_alert_deduplicated(db: Session, condition: str, metric: str, observed_value: float, threshold: float, severity: str, affected_component: str, fingerprint: str) -> MonitoringAlert:
        # Check for active alert with same fingerprint
        existing = db.query(MonitoringAlert).filter(
            MonitoringAlert.affected_component == affected_component,
            MonitoringAlert.metric == metric,
            MonitoringAlert.condition == condition,
            MonitoringAlert.status == "ACTIVE"
        ).first()
        
        if existing:
            # Deduplicate, don't create a new one, maybe just update observed_value
            existing.observed_value = observed_value
            db.commit()
            return existing
            
        # Create new
        alert = MonitoringAlert(
            condition=condition,
            metric=metric,
            observed_value=observed_value,
            threshold=threshold,
            severity=severity,
            affected_component=affected_component
        )
        db.add(alert)
        db.commit()
        return alert
