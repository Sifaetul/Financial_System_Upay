with open("tests/test_copilot.py", "r") as f:
    content = f.read()

content = content.replace('if "access_token" in resp.json():', 'print(resp.json())\n    if "access_token" in resp.json():')
with open("tests/test_copilot.py", "w") as f:
    f.write(content)
