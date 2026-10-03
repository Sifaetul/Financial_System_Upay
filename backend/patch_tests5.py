with open("tests/test_copilot.py", "r") as f:
    content = f.read()

content = content.replace('client.post("/api/v1/auth/register"', 'reg = client.post("/api/v1/auth/register"')
content = content.replace('})\n    \n    resp = client.post', '})\n    print("REG:", reg.json())\n    \n    resp = client.post')
with open("tests/test_copilot.py", "w") as f:
    f.write(content)
