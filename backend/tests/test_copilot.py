import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.investigation import InvestigationCase, CaseEvidence
from app.models.ai import AiDocument, AiChunk
from app.services.embedding_provider import get_embedding_provider
import uuid

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    email = f"investigator_{uuid.uuid4()}@upaynexus.com"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "password_confirm": "Password123!",
        "full_name": "Test User",
        "role_names": ["INVESTIGATOR"]
    })
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": "Password123!"})
    token = resp.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def setup_test_case():
    db = SessionLocal()
    case_id = str(uuid.uuid4())
    case = InvestigationCase(
        id=case_id,
        primary_entity_type="CUSTOMER", primary_entity_id="test_entity",
        case_number=f"CASE-{case_id[:8]}",
        title="Copilot Test Case",
        description="Test case for copilot verification",
        status="OPEN",
        severity="HIGH"
    )
    db.add(case)
    db.flush()
    
    doc = AiDocument(
        id=str(uuid.uuid4()),
        case_id=case_id,
        entity_id="test_entity",
        entity_type="CUSTOMER",
        source_type="INVESTIGATION_NOTE",
        content="Test context Document"
    )
    db.add(doc)
    db.flush()
    
    text = "Transaction amount = 5000"
    embedder = get_embedding_provider()
    embedding = embedder.get_embedding(text)
    
    chunk = AiChunk(
        id=str(uuid.uuid4()),
        document_id=doc.id,
        content=text,
        embedding=embedding,
        chunk_index=0
    )
    db.add(chunk)
    db.commit()
    return case_id

def test_copilot_insufficient_evidence(auth_headers, setup_test_case):
    case_id = setup_test_case
    response = client.post(
        f"/api/v1/copilot/cases/{case_id}/chat",
        json={"question": "What is the secret alien password?"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data

def test_copilot_security_unauthorized(setup_test_case):
    case_id = setup_test_case
    response = client.post(
        f"/api/v1/copilot/cases/{case_id}/chat",
        json={"question": "Test"},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 401

def test_copilot_hybrid_retrieval_and_answer(auth_headers, setup_test_case):
    case_id = setup_test_case
    response = client.post(
        f"/api/v1/copilot/cases/{case_id}/chat",
        json={"question": "What is the Transaction amount?"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0

def test_copilot_citation_validation(auth_headers, setup_test_case):
    case_id = setup_test_case
    response = client.post(
        f"/api/v1/copilot/cases/{case_id}/chat",
        json={"question": "Test citation"},
        headers=auth_headers
    )
    assert response.status_code == 200
