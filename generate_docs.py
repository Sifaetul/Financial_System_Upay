import os

base_path = "/Users/traxem_harze/Desktop/AI_Dev_Fest/docs"
os.makedirs(base_path, exist_ok=True)

files = {}

files["architecture.md"] = """
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
- Injects: Anomalies, mule patterns, ATO behaviors.
"""

files["system-flow.md"] = """
# End-to-End Data Flow

## Primary Transaction Flow

```mermaid
sequenceDiagram
    participant Source
    participant API as API Gateway
    participant DB as PostgreSQL
    participant Redis as Event Broker
    participant Feat as Feature Extractor
    participant Engine as Intelligence Engines (Rule/ML/Graph)
    participant Risk as Risk Fusion
    participant UI as Dashboard

    Source->>API: POST /transactions (Transaction Created)
    API->>API: Validate Payload
    API->>DB: Save Transaction (Status: Pending)
    API->>Redis: Publish `transaction.created`
    API-->>Source: 202 Accepted

    Redis->>Feat: Consume `transaction.created`
    Feat->>Feat: Extract Features (Velocity, Location, etc.)
    Feat->>Redis: Publish `features.extracted`

    Redis->>Engine: Consume `features.extracted`
    Engine->>Engine: Run Rules, ML Inference, Graph Traversal
    Engine->>Redis: Publish `signals.generated`

    Redis->>Risk: Consume `signals.generated`
    Risk->>Risk: Normalize, Weight, Fusion
    Risk->>DB: Save Final Risk Score & Decision
    Risk->>Redis: Publish `risk.calculated`
    
    Redis->>UI: WebSocket emit `alert.created` (if high risk)
```
"""

files["module-map.md"] = """
# Module Architecture

## Foundational Modules
- **auth:** JWT, RBAC, Passwords.
- **users:** System users, investigators.
- **audit:** System audit logs.
- **monitoring:** Health checks, metrics.

## Core Domain Modules
- **customers:** Profiles, segments.
- **accounts:** Account balances, limits.
- **transactions:** Core transaction ledger.
- **devices & locations:** Device fingerprints, Geo-IP mapping.
- **merchants & agents:** Business profiles, agent networks.

## Intelligence Modules (Core)
- **events:** Redis pub/sub routing, Celery tasks.
- **rules:** Deterministic logic.
- **fraud & anomaly:** Behavioral profiling, ML predictors.
- **graph:** NetworkX graph building, traversal.
- **risk:** Fusion engine, weighting.
- **customer_intelligence:** Customer behavior analytics.
- **financial_intelligence:** Cash flow and risk metrics.
- **merchant_intelligence:** Merchant fraud/risk monitoring.
- **agent_intelligence:** Agent network anomalies.

## AI & Investigation Modules
- **alerts:** Alert lifecycle.
- **investigations:** Case management.
- **documents & embeddings:** RAG prep, chunking.
- **ai:** Copilot chat, LLM prompt assembly.
- **feedback:** Investigator tuning.
- **simulation:** What-if scenarios, rule backtesting.

## Dependency Graph
```mermaid
graph TD
    UI --> Auth
    UI --> Alerts
    UI --> Investigations
    UI --> AI
    UI --> Transactions
    
    Investigations --> Transactions
    Investigations --> Customers
    Investigations --> Risk
    
    AI --> Documents
    AI --> Investigations
    
    Risk --> Fraud
    Risk --> Graph
    Risk --> Rules
    
    Fraud --> Transactions
    Graph --> Transactions
    Rules --> Transactions
    
    Transactions --> Events
    Events --> Auth
```

## Repository Blueprint
```text
upay_nexus/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── core/         # Config, Security, DB session
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic per module
│   │   ├── events/       # Celery tasks & Redis pubsub
│   │   └── ai/           # LLM logic & RAG
│   ├── alembic/          # Migrations
│   ├── tests/
│   └── main.py
├── frontend/             # Next.js app
├── ml/                   # Model training, jupyter notebooks
├── docker/               # Compose files, Dockerfiles
├── scripts/              # Synthetic data, management scripts
└── docs/                 # Architecture documents
```
"""

files["database-design.md"] = """
# Database Architecture (PostgreSQL + pgvector)

## Entity Relationship Model

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : has
    USERS ||--o{ AUDIT_LOGS : generates
    CUSTOMERS ||--o{ ACCOUNTS : owns
    CUSTOMERS ||--o{ CUSTOMER_PROFILES : has
    CUSTOMERS ||--o{ CUSTOMER_SEGMENTS : categorized
    ACCOUNTS ||--o{ TRANSACTIONS : sends_receives
    TRANSACTIONS ||--o{ TRANSACTION_EVENTS : tracks
    TRANSACTIONS }|--|| MERCHANTS : involves
    TRANSACTIONS }|--|| AGENTS : involves
    TRANSACTIONS }|--|| DEVICES : uses
    TRANSACTIONS }|--|| LOCATIONS : occurs_at
    TRANSACTIONS ||--o{ RISK_SCORES : has
    TRANSACTIONS ||--o{ ALERTS : triggers
    ALERTS ||--o{ CASES : linked_to
    CASES ||--o{ CASE_EVENTS : tracks
    AI_DOCUMENTS ||--o{ AI_CHUNKS : split_into
    RULES ||--o{ RULE_VERSIONS : versioned
    MODEL_REGISTRY ||--o{ MODEL_PREDICTIONS : predicts
```

## Core Tables
1. **users:** id (PK), email, password_hash, is_active.
2. **roles:** id (PK), name, permissions (JSONB).
3. **customers:** id (PK), name, kyc_status, risk_rating.
4. **accounts:** id (PK), customer_id (FK), balance, currency.
5. **transactions:** id (PK), sender_account (FK), receiver_account (FK), amount, type, status, created_at.
6. **devices/locations:** device_fingerprint (PK), ip_address, coordinates.
7. **merchants/agents:** id (PK), name, category, tier.
8. **alerts:** id (PK), transaction_id (FK), rule_triggered, severity, status.
9. **cases:** id (PK), alert_id (FK), investigator_id (FK), status, summary.
10. **risk_scores:** id (PK), transaction_id (FK), rules_score, ml_score, graph_score, final_score.
11. **rules/rule_versions:** id (PK), logic (JSON), is_active.
12. **ai_chunks:** id (PK), document_id (FK), content, embedding (VECTOR).
13. **investigator_feedback:** id (PK), case_id (FK), is_false_positive, notes.

## Security & Privacy
- **Masking:** PII (SSN, Phone, Email) masked at API layer.
- **Sensitive Data:** Encrypted at rest. Hashed passwords (bcrypt).
"""

files["api-map.md"] = """
# API Architecture (v1)

All APIs prefixed with `/api/v1`

## Authentication & Users
- `POST /auth/login` -> JWT Access & Refresh
- `GET /users/me` -> Profile & Permissions

## Core Entities
- `GET /customers/{id}` -> Customer 360
- `GET /accounts/{id}/transactions` -> Transaction history
- `POST /transactions` -> Ingest new transaction (Async)

## Intelligence & Risk
- `GET /risk/{transaction_id}` -> Detailed explainable risk score
- `GET /graph/customer/{id}` -> Network nodes and edges
- `GET /financial-intelligence/{customer_id}` -> Cash-flow forecasts
- `GET /merchant-intelligence/{id}` -> Merchant fraud/risk monitoring
- `GET /agent-intelligence/{id}` -> Agent network anomalies
- `POST /simulation/run` -> What-if scenarios, rule backtesting

## Alerts & Investigations
- `GET /alerts` -> Filtered queue for analysts
- `POST /alerts/{id}/triage` -> Update alert status
- `GET /cases/{id}` -> Investigation details
- `POST /cases/{id}/feedback` -> True/False positive submission

## AI Copilot
- `POST /ai/chat` -> Send message to case copilot
- `POST /ai/summarize/{case_id}` -> Trigger automated case summary
"""

files["event-map.md"] = """
# Event Architecture

## Event Broker: Redis + Celery
- **Producer:** FastAPI routes, Workers.
- **Consumer:** Celery Workers.

## Standard Event Schema
```json
{
  "event_id": "uuid",
  "correlation_id": "uuid",
  "trace_id": "uuid",
  "event_type": "transaction.created",
  "timestamp": "iso8601",
  "producer": "api_gateway",
  "entity_id": "txn_123",
  "payload": {}
}
```

## Core Events
- `transaction.created`: Triggers Risk, ML, Graph extraction.
- `transaction.updated`: Transaction status changes.
- `risk.calculated`: Triggers Alert evaluation.
- `alert.created`: Triggers WebSocket UI update, Case creation.
- `case.created`: Investigation case generated.
- `feedback.created`: Investigator logs feedback, triggers ML retraining loop.
- `model.prediction.created`: ML generates output.
- `customer.profile.updated`: Customer 360 updated.

## Reliability
- **Idempotency:** Consumers check DB for `event_id` before processing.
- **Retries:** Celery exponential backoff for DB/API failures. DLQ for permanent failures.
"""

files["risk-architecture.md"] = """
# Risk Engine Architecture

## Signal Pipeline
1. **Rule Score:** Deterministic checks (e.g., Velocity > 5 in 1hr -> 100 points).
2. **ML Score:** Probabilistic output (0.0 to 1.0) scaled to 1-100.
3. **Graph Score:** Network exposure score (Distance to known bad actor).
4. **Behavior Score:** Deviation from historical baseline.
5. **Device/Location Risk:** Anomalous logins, impossible travel.

## Risk Fusion Engine
- Applies dynamic weights based on transaction type/context.
- `Final Score = (W1 * Rule) + (W2 * ML) + (W3 * Graph) + (W4 * Behavior)`
- Generates **Explainability Matrix**: Top 3 contributing factors for the final score, mapped for human readability.

## Decisions
- 0-30: Allow
- 31-70: Step-up Auth (MFA)
- 71-100: Block & Alert
"""

files["ml-architecture.md"] = """
# Machine Learning Architecture

## Pipeline Lifecycle
1. **Data Ingestion:** Async job dumps transaction + feature tables.
2. **Feature Engineering:** Batch and streaming feature calculations.
3. **Dataset Creation:** Automated snapshot generation.
4. **Training:** Scikit-learn/XGBoost pipelines (Phase 6+).
5. **Validation:** Hold-out sets, precision/recall constraints.
6. **Registry:** MLflow or similar for versioning (`v1.0.0-fraud-xgb`).
7. **Deployment:** Seamless API / Worker load.
8. **Inference:** Celery worker loads model into memory.
9. **Monitoring & Drift Detection:** Distribution divergence analysis.
10. **Retraining:** Feedback loop triggered via investigator feedback.

## Explainability
- SHAP values calculated alongside prediction.
- Stored in `model_predictions` for dashboard retrieval.
"""

files["graph-architecture.md"] = """
# Graph Intelligence Architecture

## Model
- **Nodes:** Customer, Account, Device, Location, Merchant, Agent, Beneficiary.
- **Relationships:** owns, uses, sends, receives, transacts, logs_in, connected_to.

## Graph Engine (NetworkX initial)
- Loads local sub-graphs from PostgreSQL relational data on demand.
- Future: Syncs to Neo4j for deep persistent graph traversal.

## Analysis Capabilities
- **Suspicious Clusters:** N accounts sharing 1 device.
- **Fraud Rings:** Cyclic transaction paths indicating money laundering.
- **Network Exposure:** Shortest path to flagged fraud node.
- *Important Rule:* Exposure must be treated as a risk signal, NOT automatically as confirmed fraud.
"""

files["ai-architecture.md"] = """
# AI Investigation Copilot

## Architecture
User -> Auth -> Permission Check -> AI Request -> Intent Detection -> Structured Retrieval / Vector Retrieval (pgvector) -> Evidence Collection -> Context Assembly -> LLM -> Grounded Answer & Citations -> Audit Log.

## Capabilities
- Case summarization.
- Transaction explanation.
- Fraud investigation assistance.
- Timeline generation.
- Policy lookup.

## Security Constraints
- AI runs with the **User's Permissions**. It cannot access data the user cannot see.
- Explicit DB structure retrieval is done via secure Python tools, NOT raw SQL execution.
- Every response includes evidence citations.
- Complete conversation flow logged to `audit_logs`.
"""

files["security-architecture.md"] = """
# Security & RBAC Architecture

## Authentication
- JWT with short expiration (15m). HttpOnly cookie for Refresh token (7d).

## RBAC Matrix
| Role | Alerts | Cases | AI Copilot | System Config | Transactions |
|------|--------|-------|------------|---------------|--------------|
| Admin | R/W | R/W | Yes | R/W | R/W |
| Investigator | R/W | R/W | Yes | No | R/O |
| Risk Analyst | Read | Read | No | R/W (Rules) | R/O |
| Customer Support | Read | No | No | No | R/O (Masked)|
| ML/AI Analyst | Read | Read | Yes | R/W (Models)| R/O |

## Core Protections
- **SQL Injection:** Prevented via SQLAlchemy ORM.
- **Rate Limiting:** Redis-based token bucket per IP/User.
- **Secrets Management:** Environment variables, no hardcoded credentials.
- **Input Validation:** Strict Pydantic schemas.
- **Data Privacy:** Sensitive data masking on API output.
- **Audit Logging:** Immutably logs all sensitive actions.
"""

files["frontend-architecture.md"] = """
# Frontend Architecture (Next.js)

## Stack
- Next.js (App Router), React, TypeScript, Tailwind CSS.

## Pages & Components
- `/login`
- `/dashboard` (Global metrics)
- `/transactions` (Live feed)
- `/risk-dashboard` (Aggregated risk scores)
- `/fraud-dashboard` (Specific fraud metrics)
- `/customer-360/{id}`
- `/financial-health`
- `/merchant-intelligence`
- `/agent-intelligence`
- `/graph-explorer`
- `/alerts`
- `/cases`
- `/copilot` (Global widget or dedicated view)
- `/model-monitoring`
- `/simulation`
- `/audit-logs`
- `/settings`

## Core Mechanics
- **State Management:** Zustand, React Query for caching.
- **Real-time:** WebSocket connections authenticated via JWT. Listen for `alert.created`.
- **RBAC:** Component rendering blocked based on user's decoded JWT role permissions.
"""

files["testing-strategy.md"] = """
# Testing Architecture

1. **Unit Tests (Pytest):** Core business logic, rule evaluations, ML feature engineering logic. Verify individual functions mock DB/Redis.
2. **Integration Tests:** Database CRUD, Celery task execution, API routing. Tests interaction between internal components.
3. **API Tests:** Request/Response validation, authentication flows, error handling.
4. **Database Tests:** Migration verification, constraint checks.
5. **Event Tests:** Pub/Sub publish, consumption, and idempotency guarantees.
6. **ML Tests:** Inference pipeline shape constraints, threshold validation.
7. **AI Tests:** Mocked LLM responses, RAG document retrieval accuracy.
8. **Frontend Tests:** Component rendering, state transitions.
9. **E2E Tests:** Complete user flows (e.g. Txn -> Alert -> Case -> Resolution).
10. **Security & Performance:** RBAC fuzzing, Locust TPS testing.
"""

files["phase-roadmap.md"] = """
# Phase Dependency Map

## Phase 0: Architecture (Current)
- **Output:** Docs, Blueprints.

## Phase 1: Infrastructure
- **Prerequisites:** P0. **Output:** Docker, Postgres, Redis, Base Repos.

## Phase 2: Database
- **Prerequisites:** P1. **Output:** SQLAlchemy Models, Alembic.

## Phase 3: Authentication & Security
- **Prerequisites:** P2. **Output:** JWT, Users, RBAC.

## Phase 4: Event Platform
- **Prerequisites:** P2. **Output:** Celery, Redis PubSub.

## Phase 5: Risk Engine
- **Prerequisites:** P4. **Output:** Rules engine, Risk Fusion framework.

## Phase 6-10: Intelligence Modules
- **Prerequisites:** P5. **Output:** Fraud, Graph, Customer, Financial, Merchant modules.

## Phase 11: Alert & Investigation
- **Prerequisites:** P5, P6. **Output:** Case Management APIs.

## Phase 12: AI Copilot
- **Prerequisites:** P11. **Output:** RAG, LLM integration.

## Phase 13-18: Finalization
- **Prerequisites:** P12. **Output:** Monitoring, UI integration, Testing, Deployment.
"""

files["feature-matrix.md"] = """
# Feature Completion Matrix

| Feature | DB | Backend | API | Event | ML | Graph | AI | WS | UI | Tests | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ingest Txn | Pending | Pending | Pending | Pending | N/A | N/A | N/A | Pending | Pending | Pending | PHASE 0 |
| RBAC Auth | Pending | Pending | Pending | N/A | N/A | N/A | N/A | N/A | Pending | Pending | PHASE 0 |
| Rules Engine | Pending | Pending | Pending | Pending | N/A | N/A | N/A | N/A | Pending | Pending | PHASE 0 |
| Risk Fusion | Pending | Pending | Pending | Pending | N/A | N/A | N/A | N/A | Pending | Pending | PHASE 0 |
| ML Inference | Pending | Pending | Pending | Pending | Pending | N/A | N/A | N/A | Pending | Pending | PHASE 0 |
| Graph Score | Pending | Pending | Pending | Pending | N/A | Pending | N/A | N/A | Pending | Pending | PHASE 0 |
| AI Copilot | Pending | Pending | Pending | N/A | N/A | N/A | Pending | N/A | Pending | Pending | PHASE 0 |
| Alerts / Cases| Pending | Pending | Pending | Pending | N/A | N/A | N/A | Pending | Pending | Pending | PHASE 0 |
"""

files["decision-log.md"] = """
# Architectural Decision Log

1. **PostgreSQL vs NoSQL:** Chosen PostgreSQL for ACID compliance on transactions and robust relational queries for investigations. pgvector added for AI.
2. **NetworkX vs Neo4j:** NetworkX chosen for Phase 0-7 to avoid operational complexity and heavy infrastructure on Day 1. Architecture is explicitly abstracted to allow a swap to Neo4j.
3. **FastAPI vs Django:** FastAPI chosen for native async support, event-driven performance, and built-in OpenAPI schema for ML integration.
4. **Celery/Redis vs Kafka:** Celery+Redis chosen for simpler local/docker footprint. Can upgrade to Kafka if throughput demands require horizontal scaling beyond Redis capabilities.
"""

files["project-state.md"] = """
# PROJECT STATE

- **Current Phase:** 0
- **Completed Phases:** None
- **Active Phase:** Phase 0
- **Completed Features:** None
- **Incomplete Features:** All documented in feature matrix
- **Database Status:** Architecture complete, not implemented
- **Backend Status:** Architecture complete, not implemented
- **Frontend Status:** Architecture complete, not implemented
- **ML Status:** Architecture complete, not implemented
- **AI Status:** Architecture complete, not implemented
- **Event System Status:** Architecture complete, not implemented
- **Graph Status:** Architecture complete, not implemented
- **Testing Status:** Architecture complete, not implemented
- **Known Issues:** None
- **Architecture Decisions:** Documented in decision-log.md
- **Next Phase:** Phase 1
- **Last Verification:** Architecture documented
"""

for k, v in files.items():
    with open(os.path.join(base_path, k), "w") as f:
        f.write(v.strip() + "\\n")
