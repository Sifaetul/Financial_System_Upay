with open("tests/test_risk_engine.py", "r") as f:
    content = f.read()

setup_tx = """
    from app.models.customer import Customer, Account
    from app.models.transaction import Transaction
    import uuid
    
    cust = Customer(identifier=str(uuid.uuid4()))
    db_session.add(cust)
    db_session.commit()
    db_session.refresh(cust)
    
    acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db_session.add(acc)
    db_session.commit()
    db_session.refresh(acc)
    
    tx = Transaction(amount=100.0, currency="USD", transaction_type="SEND_MONEY", sender_account_id=acc.id, receiver_account_id=acc.id, status="RECEIVED", idempotency_key=str(uuid.uuid4()))
    db_session.add(tx)
    db_session.commit()
    db_session.refresh(tx)
    
    context = RiskContext(
        transaction_id=tx.id, amount=100.0, currency="USD",
        transaction_type="SEND_MONEY", timestamp=datetime.now(UTC),
        correlation_id="corr_1"
    )
"""

import re
content = re.sub(r"    context = RiskContext.*?correlation_id=\"corr_1\"\n    \)", setup_tx, content, flags=re.DOTALL)

with open("tests/test_risk_engine.py", "w") as f:
    f.write(content)
