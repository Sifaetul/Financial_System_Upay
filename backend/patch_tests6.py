with open("tests/test_copilot.py", "r") as f:
    content = f.read()

content = content.replace('"password": "Password123!", "full_name"', '"password": "Password123!", "password_confirm": "Password123!", "full_name"')
with open("tests/test_copilot.py", "w") as f:
    f.write(content)
