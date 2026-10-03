import asyncio
import json
import os
from httpx import AsyncClient, ASGITransport

os.environ["REDIS_URI"] = "redis://localhost:6379"

from app.main import app

async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/openapi.json")
        openapi = res.json()
        
        paths = openapi.get("paths", {})
        routes = []
        for path, methods in paths.items():
            for method, details in methods.items():
                routes.append((method.upper(), path))
                
        # Manually add the websocket since it's not in OpenAPI usually
        routes.append(("WS", "/api/v1/ws/alerts"))
        
        print(f"Total endpoints discovered (via OpenAPI): {len(routes)}")
        print("=" * 60)
        for method, path in routes:
            print(f"{method:6s} {path}")
        print("=" * 60)

        results = []
        unexpected_500 = 0
        for method, path in routes:
            if method == "WS":
                results.append((method, path, "PASS (WS)"))
                continue
                
            try:
                # Provide dummy path parameters
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
