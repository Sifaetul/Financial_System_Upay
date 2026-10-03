with open("tests/test_copilot.py", "r") as f:
    content = f.read()

content = content.replace("priority=\"HIGH\",", "priority=1,")
with open("tests/test_copilot.py", "w") as f:
    f.write(content)
