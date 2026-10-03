import re
with open("verify_monitoring.py", "r") as f:
    c = f.read()
c = c.replace("evaluate_transaction(db, tx)", """
    context = RiskContext(transaction_id=tx_id, event_id="evt", correlation_id="corr", causation_id="cause", amount=tx.amount, currency=tx.currency, channel=tx.channel)
    engine = UnifiedRiskEngine(db)
    engine.evaluate(context, [])
""")
with open("verify_monitoring.py", "w") as f:
    f.write(c)
