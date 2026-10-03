with open("app/worker.py", "r") as f:
    content = f.read()
content = content.replace("from app.models.customer import AccountEvent\n", "")
with open("app/worker.py", "w") as f:
    f.write(content)
