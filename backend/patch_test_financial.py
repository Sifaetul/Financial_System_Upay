with open("tests/test_financial_intelligence.py", "r") as f:
    content = f.read()

old_env = """def create_customer_env(db):
    cust = Customer(identifier=str(uuid.uuid4()))
    db.add(cust)
    db.commit()
    
    acc1 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    acc2 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    ext_acc = Account(customer_id=str(uuid.uuid4()), account_number_hash=str(uuid.uuid4()))
    
    db.add_all([acc1, acc2, ext_acc])
    db.commit()
    return cust.id, acc1.id, acc2.id, ext_acc.id"""

new_env = """def create_customer_env(db):
    cust = Customer(identifier=str(uuid.uuid4()))
    ext_cust = Customer(identifier=str(uuid.uuid4()))
    db.add_all([cust, ext_cust])
    db.commit()
    
    acc1 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    acc2 = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    ext_acc = Account(customer_id=ext_cust.id, account_number_hash=str(uuid.uuid4()))
    
    db.add_all([acc1, acc2, ext_acc])
    db.commit()
    return cust.id, acc1.id, acc2.id, ext_acc.id"""

content = content.replace(old_env, new_env)

with open("tests/test_financial_intelligence.py", "w") as f:
    f.write(content)
