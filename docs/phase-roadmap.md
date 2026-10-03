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
- **Prerequisites:** P12. **Output:** Monitoring, UI integration, Testing, Deployment.\n