# UPAY NEXUS AI — Final Known Limitations

## 1. Implemented
- **Graph Intelligence:** Fan-in and Fan-out detection are fully implemented and verified via deterministic local rules within PostgreSQL and NetworkX.
- **AI Copilot:** Hybrid retrieval and RAG architectures are fully implemented using real local embeddings and HuggingFace pipelines.
- **Real-Time Websockets:** Alerts broadcast correctly via FastAPI WebSockets.

## 2. Verified
- **Production Fail-Safes:** The application correctly crashes if `SECRET_KEY` is weak or `DATABASE_URI` is pointing to localhost without explicit overrides.
- **Rate Limiting:** Fully verified to trigger `429 Too Many Requests` accurately using Redis.

## 3. Environment-Dependent
- **Celery Tasks:** In testing, tasks may execute synchronously or asynchronously depending on the `CELERY_TASK_ALWAYS_EAGER` environment variable.
- **Rate Limiter Bypass:** The `TESTING=1` environment variable bypasses the global rate limiter to allow the `pytest` regression suite to finish without throwing `429` errors.

## 4. External Dependency
- **AI Models:** The Copilot depends on HuggingFace `all-MiniLM-L6-v2` for embeddings. If HuggingFace is down, initial model download may fail in isolated environments.

## 5. Future Enhancement
- **Kubernetes Scaling:** Currently deployed on Docker Compose. Scaling to Kubernetes with Helm charts would be required for extreme high-availability horizontal scaling.
- **Graph Database:** NetworkX and PostgreSQL are sufficient for the competition, but moving to Neo4j or Amazon Neptune would improve massive-scale deep graph traversals.
- **Distributed Tracing:** Currently tracing uses `X-Request-ID` and JSON logging. Full OpenTelemetry integration with Jaeger/Zipkin would enhance observability.
