import sys
import os
import json
import uuid

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.database import SessionLocal
from app.models.investigation import InvestigationCase, CaseEvidence
from app.models.ai import AiDocument, AiChunk
from app.services.copilot_service import CopilotService
from app.services.embedding_provider import get_embedding_provider
from app.services.llm_provider import get_llm_provider

def verify_all():
    db = SessionLocal()
    case_id = str(uuid.uuid4())
    case = InvestigationCase(
        id=case_id,
        primary_entity_type="CUSTOMER",
        primary_entity_id="test_customer_123",
        case_number=f"CASE-{case_id[:8]}",
        title="Copilot E2E Verification",
        description="Verification case",
        status="OPEN",
        severity="HIGH"
    )
    db.add(case)
    db.commit()

    doc = AiDocument(
        id=str(uuid.uuid4()),
        case_id=case_id,
        entity_id="test_customer_123",
        entity_type="CUSTOMER",
        source_type="INVESTIGATION_NOTE",
        content="Transaction amount was 5000 BDT."
    )
    db.add(doc)
    db.commit()

    embedder = get_embedding_provider()
    embedding = embedder.get_embedding(doc.content)

    chunk = AiChunk(
        id=str(uuid.uuid4()),
        document_id=doc.id,
        content=doc.content,
        embedding=embedding,
        chunk_index=0
    )
    db.add(chunk)
    db.commit()

    service = CopilotService(db)
    user_id = str(uuid.uuid4())
    
    # Send a prompt 
    response = service.process_chat(
        case_id=case_id,
        user_id=user_id,
        question="What was the transaction amount?"
    )

    print("--- E2E RESPONSE ---")
    print(json.dumps(response.dict(), indent=2))
    
    print("--- CITATION SECURITY CHECK ---")
    valid = service._validate_citations(case_id, [{"source_type": "CHUNK", "source_id": chunk.id}])
    print("Valid citation check:", len(valid) == 1)
    
    invalid = service._validate_citations(case_id, [{"source_type": "CHUNK", "source_id": str(uuid.uuid4())}])
    print("Invalid citation check:", len(invalid) == 0)

if __name__ == "__main__":
    verify_all()
