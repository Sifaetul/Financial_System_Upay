with open("app/api/v1/router.py", "r") as f:
    content = f.read()

if "from .endpoints import financial" not in content:
    content = content.replace("from .endpoints import customer", "from .endpoints import customer\nfrom .endpoints import financial")
    content += "\napi_router.include_router(financial.router, prefix=\"/customers\", tags=[\"financial\"])\n"

with open("app/api/v1/router.py", "w") as f:
    f.write(content)
