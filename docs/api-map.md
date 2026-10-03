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
- `POST /ai/summarize/{case_id}` -> Trigger automated case summary\n