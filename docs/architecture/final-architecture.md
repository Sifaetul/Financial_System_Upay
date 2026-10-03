# UPAY NEXUS AI — Final Architecture

```text
Frontend (Next.js 14, TailwindCSS, React Force Graph)
   │
   ▼
API Gateway / Reverse Proxy (Docker Exposed Port 8000)
   │
   ▼
FastAPI (Gunicorn + Uvicorn Workers)
   │
   ├─► Event Platform (REST / Background Tasks)
   │
   ├─► Unified Intelligence Layer
   │      ├─ Fraud (Velocity, ATO, Rules)
   │      ├─ Graph (NetworkX, Shared Entities)
   │      ├─ Customer (Lifecycle, Segmentation)
   │      ├─ Financial (Stress, Liquidity)
   │      ├─ Merchant (Anomalies)
   │      └─ Agent (Location Anomalies)
   │
   ├─► Risk Fusion (Weighted Explainable Context)
   │
   ├─► Alerts & Investigation (Celery Async Worker / Websockets)
   │
   ├─► AI Copilot (RAG, Local Embeddings, pgvector)
   │
   ├─► Competition Intelligence (Simulator, Replay)
   │
   └─► Monitoring & Governance (Liveness, Readiness, Audit)

Databases & Message Brokers:
- PostgreSQL 16 (Relational Data, JSONB, pgvector)
- Redis 7 (Rate Limiting, Celery Broker, Websocket PubSub proxy mapping)
```

## Highlights
- **PostgreSQL / pgvector:** The single source of truth for all domain entities, risk snapshots, audits, and vector embeddings for the AI Copilot.
- **Redis:** Serves as the high-throughput message broker for Celery and the distributed lock/store for FastAPI global rate limiting.
- **Celery:** Offloads heavy intelligence processing (e.g. Graph fan-in logic) and AI embedding generation to a background worker to keep the API ultra-responsive.
- **WebSocket:** Streams real-time alerts directly from the backend context to the Next.js frontend to allow investigators instant situational awareness.
