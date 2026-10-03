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
- **Retries:** Celery exponential backoff for DB/API failures. DLQ for permanent failures.\n