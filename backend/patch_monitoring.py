import re
with open("app/services/monitoring_service.py", "r") as f:
    c = f.read()

# Replace get_health to verify redis/etc
health_orig = """        # Check DB
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
            health["status"] = "degraded\"\"\""""

# Let's just redefine create_alert to deduplicate, and run_drift_detection.

c += """

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
"""

with open("app/services/monitoring_service.py", "w") as f:
    f.write(c)
