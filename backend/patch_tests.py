with open("tests/test_copilot.py", "r") as f:
    content = f.read()
content = content.replace("from app.db.session import SessionLocal", "from app.core.database import SessionLocal")
with open("tests/test_copilot.py", "w") as f:
    f.write(content)
