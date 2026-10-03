with open("app/api/v1/router.py", "r") as f:
    content = f.read()

if "from .endpoints import merchant" not in content:
    content = content.replace("from .endpoints import financial", "from .endpoints import financial\nfrom .endpoints import merchant\nfrom .endpoints import agent")
    content += "\napi_router.include_router(merchant.router, prefix=\"/merchants\", tags=[\"merchants\"])\n"
    content += "api_router.include_router(agent.router, prefix=\"/agents\", tags=[\"agents\"])\n"

with open("app/api/v1/router.py", "w") as f:
    f.write(content)
