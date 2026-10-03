with open("tests/test_copilot.py", "r") as f:
    content = f.read()

content = content.replace("db.add(case)\n    \n    doc", "db.add(case)\n    db.flush()\n    doc")
with open("tests/test_copilot.py", "w") as f:
    f.write(content)
