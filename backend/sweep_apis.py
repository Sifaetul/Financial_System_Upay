import sys
import os
import asyncio
from httpx import AsyncClient, ASGITransport

os.environ["REDIS_URI"] = "redis://localhost:6379"

try:
    from app.main import app
except Exception as e:
    print(f"Error loading app: {e}")
    sys.exit(1)

def get_routes(app):
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                if method not in ["OPTIONS", "HEAD"]:
                    routes.append((method, route.path))
        elif type(route).__name__ == "WebSocketRoute":
            routes.append(("WS", route.path))
    return routes

async def main():
    routes = get_routes(app)
    print(f"Total endpoints discovered: {len(routes)}")
    print("=" * 60)
    for method, path in routes:
        print(f"{method:6s} {path}")
    print("=" * 60)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        results = []
        unexpected_500 = 0
        for method, path in routes:
            if method == "WS":
                results.append((method, path, "PASS (WS)"))
                continue
                
            try:
                # Provide dummy path parameters if needed
                test_path = path.replace("{", "").replace("}", "")
                if method == "GET":
                    res = await client.get(test_path)
                elif method == "POST":
                    res = await client.post(test_path, json={})
                elif method == "PUT":
                    res = await client.put(test_path, json={})
                elif method == "PATCH":
                    res = await client.patch(test_path, json={})
                elif method == "DELETE":
                    res = await client.delete(test_path)
                
                if res.status_code >= 500:
                    unexpected_500 += 1
                    status = f"FAIL {res.status_code}"
                else:
                    status = f"PASS {res.status_code}"
                
                results.append((method, path, status))
            except Exception as e:
                unexpected_500 += 1
                results.append((method, path, f"FAIL ERROR: {e}"))
                
    print("\nSweep Results (Unauthenticated, Empty JSON, Dummy Path Params):")
    for method, path, status in results:
        print(f"{status:10s} | {method:6s} | {path}")

    print(f"\nUnexpected 5xx count: {unexpected_500}")

if __name__ == "__main__":
    asyncio.run(main())
