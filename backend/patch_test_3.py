with open("tests/test_investigation.py", "r") as f:
    content = f.read()

content = content.replace("transaction_id=tx_id,", "transaction_id=tx_id, event_id=tx_id,")
content = content.replace("score=85.0", "risk_score=85.0")

with open("tests/test_investigation.py", "w") as f:
    f.write(content)
