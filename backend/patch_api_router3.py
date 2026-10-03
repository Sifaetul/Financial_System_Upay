with open("app/api/v1/router.py", "r") as f:
    content = f.read()
if "from .endpoints import copilot" not in content:
    content = content.replace("from .endpoints import investigation\n", "from .endpoints import investigation\nfrom .endpoints import copilot\n")
with open("app/api/v1/router.py", "w") as f:
    f.write(content)
