with open("backend/app/api/deps.py", "r") as f:
    content = f.read()

# Replace strict check with wildcard check
content = content.replace(
    "if req not in user_perms:\n                raise HTTPException",
    "if req not in user_perms and '*' not in user_perms:\n                raise HTTPException"
)

with open("backend/app/api/deps.py", "w") as f:
    f.write(content)
