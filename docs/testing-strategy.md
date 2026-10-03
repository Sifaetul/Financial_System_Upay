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
10. **Security & Performance:** RBAC fuzzing, Locust TPS testing.\n