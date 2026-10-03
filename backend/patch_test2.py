with open("tests/test_copilot.py", "r") as f:
    content = f.read()

auth_fix = """@pytest.fixture(scope="module")
def auth_headers():
    import uuid
    email = f"investigator_{uuid.uuid4()}@upaynexus.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "password_confirm": "Password123!",
        "full_name": "Test User",
        "role_names": ["INVESTIGATOR"]
    })
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": "Password123!"})
    token = resp.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}
"""

import re
content = re.sub(r'@pytest\.fixture\(scope="module"\)\ndef auth_headers\(\):.*?return {"Authorization": f"Bearer \{token\}"}', auth_fix, content, flags=re.DOTALL)

content = content.replace('assigned_to=None', 'assigned_to_id=None')

with open("tests/test_copilot.py", "w") as f:
    f.write(content)
