with open("tests/test_investigation.py", "r") as f:
    content = f.read()

content = content.replace("from app.models.auth import User", "from app.models.identity import User")

with open("tests/test_investigation.py", "w") as f:
    f.write(content)
