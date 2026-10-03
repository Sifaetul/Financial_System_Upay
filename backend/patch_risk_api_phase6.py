with open("app/api/v1/endpoints/risk.py", "r") as f:
    content = f.read()

content = content.replace(
    "from app.services.risk_engine import UnifiedRiskEngine, RiskSignalCollector, amount_velocity_provider, location_anomaly_provider",
    "from app.services.risk_engine import UnifiedRiskEngine\nfrom app.services.fraud_intelligence import FraudIntelligenceOrchestrator"
)

old_block = """        collector = RiskSignalCollector()
        collector.register_provider(amount_velocity_provider)
        collector.register_provider(location_anomaly_provider)
        signals = collector.collect(context)"""

new_block = """        signals = FraudIntelligenceOrchestrator.evaluate(db, req.transaction_id, context.correlation_id)"""

content = content.replace(old_block, new_block)

with open("app/api/v1/endpoints/risk.py", "w") as f:
    f.write(content)
