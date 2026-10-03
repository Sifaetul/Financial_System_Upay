with open("app/worker.py", "r") as f:
    content = f.read()

imports = "from app.models.transaction import TransactionEvent\nfrom app.models.customer import Account\n"
content = imports + content
with open("app/worker.py", "w") as f:
    f.write(content)
