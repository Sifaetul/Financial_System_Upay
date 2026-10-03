# Architectural Decision Log

1. **PostgreSQL vs NoSQL:** Chosen PostgreSQL for ACID compliance on transactions and robust relational queries for investigations. pgvector added for AI.
2. **NetworkX vs Neo4j:** NetworkX chosen for Phase 0-7 to avoid operational complexity and heavy infrastructure on Day 1. Architecture is explicitly abstracted to allow a swap to Neo4j.
3. **FastAPI vs Django:** FastAPI chosen for native async support, event-driven performance, and built-in OpenAPI schema for ML integration.
4. **Celery/Redis vs Kafka:** Celery+Redis chosen for simpler local/docker footprint. Can upgrade to Kafka if throughput demands require horizontal scaling beyond Redis capabilities.\n