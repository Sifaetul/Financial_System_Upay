with open("app/api/v1/router.py", "r") as f:
    content = f.read()

if "endpoints.copilot" not in content:
    content = content.replace(
        "from .endpoints import auth, transactions, customer, graph, merchant, agent, financial, fraud, risk, investigation",
        "from .endpoints import auth, transactions, customer, graph, merchant, agent, financial, fraud, risk, investigation, copilot"
    )
    content += "\napi_router.include_router(copilot.router, prefix='/copilot', tags=['copilot'])\n"

with open("app/api/v1/router.py", "w") as f:
    f.write(content)
