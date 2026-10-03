with open("app/api/v1/router.py", "r") as f:
    content = f.read()

if "from .endpoints import graph" not in content:
    content = content.replace("from .endpoints import fraud", "from .endpoints import fraud\nfrom .endpoints import graph")
    content += "\napi_router.include_router(graph.router, prefix=\"/graph\", tags=[\"graph\"])\n"

with open("app/api/v1/router.py", "w") as f:
    f.write(content)
