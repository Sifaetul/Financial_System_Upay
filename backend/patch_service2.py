with open("app/services/transaction_service.py", "r") as f:
    content = f.read()

content = content.replace("self.db.add(new_tx)", "new_tx.id = str(uuid.uuid4())\n        self.db.add(new_tx)")

with open("app/services/transaction_service.py", "w") as f:
    f.write(content)
