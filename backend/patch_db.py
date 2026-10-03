with open("tests/test_db.py", "r") as f:
    content = f.read()

content = content.replace("saved_txn = db.query(Transaction).first()", "saved_txn = db.query(Transaction).filter_by(id=txn.id).first()")

with open("tests/test_db.py", "w") as f:
    f.write(content)
