with open("app/api/v1/router.py", "r") as f:
    content = f.read()
if "from .endpoints import risk" not in content:
    content = content.replace("from .endpoints import auth, transactions", "from .endpoints import auth, transactions, risk")
    content = content.replace("api_router.include_router(transactions.router, prefix=\"/transactions\", tags=[\"transactions\"])", "api_router.include_router(transactions.router, prefix=\"/transactions\", tags=[\"transactions\"])\napi_router.include_router(risk.router, prefix=\"/risk\", tags=[\"risk\"])")
    with open("app/api/v1/router.py", "w") as f:
        f.write(content)
