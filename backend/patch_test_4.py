with open("tests/test_investigation.py", "r") as f:
    content = f.read()

imports = "from app.models.transaction import Transaction\n"
if "from app.models.transaction import Transaction" not in content:
    content = imports + content

transaction_mock = """
    tx_id = str(uuid.uuid4())
    tx = Transaction(id=tx_id, sender_account_id=str(uuid.uuid4()), receiver_account_id=str(uuid.uuid4()), amount=100.0, currency='USD', transaction_type='TRANSFER', status='COMPLETED')
    db.add(tx)
    db.commit()
"""

content = content.replace("    tx_id = str(uuid.uuid4())", transaction_mock)

with open("tests/test_investigation.py", "w") as f:
    f.write(content)
