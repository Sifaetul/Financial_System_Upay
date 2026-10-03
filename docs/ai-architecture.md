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
- Complete conversation flow logged to `audit_logs`.\n