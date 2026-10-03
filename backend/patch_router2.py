with open("app/api/v1/router.py", "r") as f:
    content = f.read()
if "from .endpoints import risk" not in content:
    content = content.replace("from .endpoints import transactions", "from .endpoints import transactions\nfrom .endpoints import risk")
    with open("app/api/v1/router.py", "w") as f:
        f.write(content)
