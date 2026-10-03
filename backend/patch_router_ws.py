with open("app/api/v1/router.py", "r") as f:
    content = f.read()

if "from .websockets import router as ws_router" not in content:
    content = "from .websockets import router as ws_router\n" + content
    content += "\napi_router.include_router(ws_router, prefix=\"/ws\", tags=[\"websockets\"])\n"

with open("app/api/v1/router.py", "w") as f:
    f.write(content)
