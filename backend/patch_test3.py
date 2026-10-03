with open("tests/test_copilot.py", "r") as f:
    content = f.read()

content = content.replace('            assigned_to_id=None\n', '')
content = content.replace('            assigned_to=None\n', '')

with open("tests/test_copilot.py", "w") as f:
    f.write(content)
