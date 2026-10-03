with open("app/api/v1/router.py", "r") as f:
    content = f.read()

if "from .endpoints import investigation" not in content:
    content = content.replace("from .endpoints import agent", "from .endpoints import agent\nfrom .endpoints import investigation")
    content += "\napi_router.include_router(investigation.router, prefix=\"/investigation\", tags=[\"investigation\"])\n"

with open("app/api/v1/router.py", "w") as f:
    f.write(content)
