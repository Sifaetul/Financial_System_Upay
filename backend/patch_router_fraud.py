with open("app/api/v1/router.py", "r") as f:
    content = f.read()
if "from .endpoints import fraud" not in content:
    content = content.replace("from .endpoints import risk", "from .endpoints import risk\nfrom .endpoints import fraud")
    content += "\napi_router.include_router(fraud.router, prefix=\"/fraud\", tags=[\"fraud\"])\n"
    with open("app/api/v1/router.py", "w") as f:
        f.write(content)
