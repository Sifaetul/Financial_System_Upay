with open("app/worker.py", "r") as f:
    content = f.read()

# Replace dummy collector import
content = content.replace(
    "from app.services.risk_engine import UnifiedRiskEngine, RiskSignalCollector, amount_velocity_provider, location_anomaly_provider",
    "from app.services.risk_engine import UnifiedRiskEngine\nfrom app.services.fraud_intelligence import FraudIntelligenceOrchestrator"
)

# Replace risk processing block
old_block = """
        collector = RiskSignalCollector()
        collector.register_provider(amount_velocity_provider)
        collector.register_provider(location_anomaly_provider)
        signals = collector.collect(context)
"""

new_block = """
        signals = FraudIntelligenceOrchestrator.evaluate(db, transaction_id, correlation_id)
"""

content = content.replace(old_block, new_block)

with open("app/worker.py", "w") as f:
    f.write(content)
