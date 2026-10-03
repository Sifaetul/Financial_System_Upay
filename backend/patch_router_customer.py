with open("app/api/v1/router.py", "r") as f:
    content = f.read()

if "from .endpoints import customer" not in content:
    content = content.replace("from .endpoints import graph", "from .endpoints import graph\nfrom .endpoints import customer")
    content += "\napi_router.include_router(customer.router, prefix=\"/customers\", tags=[\"customers\"])\n"

with open("app/api/v1/router.py", "w") as f:
    f.write(content)
