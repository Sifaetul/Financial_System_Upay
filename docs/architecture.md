# System Architecture Blueprint

## Core Principle
**ONE EVENT → MULTIPLE INTELLIGENCE → ONE EXPLAINABLE DECISION**

## Technology Stack
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database:** PostgreSQL (with pgvector for embeddings)
- **Event/Async:** Redis (Broker/Cache), Celery (Workers), WebSockets
- **Machine Learning:** NumPy, Pandas, scikit-learn, XGBoost / LightGBM, SHAP
- **Graph:** NetworkX (architecture allows future Neo4j integration)
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Deployment:** Docker, Docker Compose

## Component Architecture

```mermaid
flowchart TD
    User([User/Client/API]) --> API_GW[FastAPI Gateway]
    API_GW --> Auth[Auth Module]
    API_GW --> EventProc[Synchronous API / Validation]
    
    EventProc --> DB[(PostgreSQL)]
    EventProc --> RedisBroker[(Redis Broker)]
    
    RedisBroker --> WorkerRules[Celery Worker - Rules]
    RedisBroker --> WorkerML[Celery Worker - ML Inference]
    RedisBroker --> WorkerGraph[Celery Worker - Graph]
    RedisBroker --> WorkerRisk[Celery Worker - Risk Fusion]
    
    WorkerRules --> RiskEngine[Risk Fusion Engine]
    WorkerML --> RiskEngine
    WorkerGraph --> RiskEngine
    
    RiskEngine --> RedisBroker
    RedisBroker --> WorkerAlert[Celery Worker - Alerts & Cases]
    
    WorkerAlert --> WS[WebSocket Server]
    WS --> UI([Frontend Dashboard])
    
    UI --> AICopilot[AI Copilot API]
    AICopilot --> VectorDB[(pgvector)]
    AICopilot --> LLM([LLM Service])
```

## Failure / Fallback Architecture
- **ML Unavailable:** Engine falls back to Rules + Deterministic signals.
- **Graph Unavailable:** Graph signals omitted; Risk Fusion adjusts weights to remaining signals.
- **LLM Unavailable:** Structured investigation tools (rules/DB query) continue working; AI chat disabled.
- **Vector Search Unavailable:** Fallback to structured SQL text search.
- **Forecasting Unavailable:** Historical trend analytics are displayed instead.

## Observability Architecture
- **Logs:** Application logs with JSON formatting, Audit Logs for sensitive operations.
- **Tracing:** Request IDs, Correlation IDs (event flow), Trace IDs (distributed).
- **Metrics:** Request latency, queue length, ML inference times, Error rates.

## Synthetic Data Generator
- Dedicated CLI/module `synthetic_gen`.
- Generates: Customers, accounts, randomized realistic transactions.
- Injects: Anomalies, mule patterns, ATO behaviors.\n