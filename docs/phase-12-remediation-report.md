# PHASE 12 REMEDIATION REPORT

## A. Fixed Blockers
- **Fake Embeddings → REAL**: Replaced `[0.01] * 1536` with a fully operational local `SentenceTransformer` (`all-MiniLM-L6-v2`) via a `LocalEmbeddingProvider`.
- **Fake Vector Search → REAL**: Downsized the `Vector` column to `384` dimensions in PostgreSQL to match the local embedder, executing genuine cosine distance computations in the database.
- **Hardcoded AI Answers → REAL**: Replaced string-matching mocks with a real offline LLM provider (`HuggingFaceTB/SmolLM2-135M`) that runs dynamic inference via Hugging Face `transformers.pipeline`.
- **Citation Bypass → REAL**: Ripped out the backdoor (`is_valid = True`) in `CopilotService`. The system now rigorously checks the source type against `Transaction`, `CaseEvidence`, and `AiChunk` (joined with `AiDocument` matching the `case_id`).

## B. Embedding Details
- **Provider**: Local (Hugging Face `sentence-transformers`) or OpenAI if configured.
- **Model**: `all-MiniLM-L6-v2` (Local fallback).
- **Dimensions**: `384`.
- **Storage**: `ai_chunks` table utilizing pgvector `VECTOR(384)`.
- **Reindexing Strategy**: An alembic migration was executed (`resize_vector_to_384`). Legacy `[0.01]*1536` fake embeddings were truncated/dropped during the column resize.

## C. Vector Search Details
- **Engine**: PostgreSQL with `pgvector`.
- **Similarity Metric**: Cosine Distance (`order_by(AiChunk.embedding.cosine_distance(query))`).
- **Authorization Filtering**: Explicitly joined against `AiDocument` where `AiDocument.case_id == current_case_id`. 
- **Semantic Retrieval Test**: Validated natively in `test_copilot_hybrid_retrieval_and_answer`.

## D. LLM Details
- **Provider**: Local (Hugging Face `transformers.pipeline`) or OpenAI if API key is present.
- **Model**: `HuggingFaceTB/SmolLM2-135M`.
- **Backend Integration**: Runs within `get_llm_provider()` abstract factory. The frontend only communicates with the Copilot API, completely shielding the model execution and preventing secret leakage.
- **Failure Handling**: Broad `try-except` blocks gracefully return a localized JSON structure indicating `"Model inference failed"`.

## E. Citation Security
- **Valid Citation**: Checked securely against `CaseEvidence`, `Transaction`, or `AiChunk` ownership.
- **Nonexistent / Unauthorized / Spoofed**: Automatically dropped from the valid citations list in `CopilotService` before persistence or frontend broadcast.
- **Cross-case Citation**: Dropped (Explicit `case_id` check in `CaseEvidence` and `AiDocument` filters).

## F. Grounding
- **Evidence exists**: Prompt includes `--- STRUCTURED EVIDENCE ---` and `--- SEMANTIC EVIDENCE ---` (with Graph limits).
- **No evidence**: The LLM provider statically injects `Insufficient evidence to answer this question.` if the retrieved semantic and structured context is completely empty.
- **Temporal/Conflict**: Treated purely as data; system prompt instructs LLM to act only on facts.

## G. Real E2E
The remediation flow generated real IDs during test cases:
- `Case ID`: dynamically generated UUID.
- `Message ID` and `Conversation ID`: generated per session.
- Citations naturally dropped or mapped based on realistic lookup.

## H. Test Results
```text
Backend:
47 passed / 0 failed (including fully re-run test_copilot.py)

RAG:
1 passed / 0 failed

Citation:
1 passed / 0 failed

Security:
1 passed / 0 failed

E2E:
1 passed / 0 failed

Frontend:
Not executed locally (Next.js layout embedded in backend test proxy)

Migration:
PASS (resize_vector_to_384 applied)

Build:
PASS
```

## I. Remaining Limitations
- The local fallback model (`SmolLM2-135M`) is incredibly small and cannot natively produce structured JSON. A parsing wrapper was created to adapt its raw text output into the expected JSON format. In a true production rollout, a 7B parameter model (e.g., Llama 3 8B or external API) is recommended for stable JSON compliance.
