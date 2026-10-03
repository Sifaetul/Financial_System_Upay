import pytest
import uuid
from fastapi.testclient import TestClient
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from app.main import app
from app.models.identity import User, Role, user_roles
from app.models.transaction import Transaction
from app.models.customer import Account, Customer
from app.models.risk import RiskEvaluation
from app.models.intelligence import GraphNode, GraphEdge
from app.core.database import SessionLocal

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture
def admin_user(db_session: Session):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"admin_{user_id}@test.com",
        password_hash="hashed",
        is_active=True
    )
    admin_role = db_session.query(Role).filter(Role.name == "ADMIN").first()
    if not admin_role:
        admin_role = Role(id=str(uuid.uuid4()), name="ADMIN")
        db_session.add(admin_role)
    user.roles.append(admin_role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_transaction(db_session: Session):
    # Create customer, account, transaction

    cust_id = str(uuid.uuid4())
    customer = Customer(id=cust_id, identifier=f"INT_{cust_id}", status="ACTIVE")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    
    acc_id = str(uuid.uuid4())
    account = Account(id=acc_id, customer_id=cust_id, account_number_hash=f"12345_{acc_id}", balance=1000.0, currency="USD", status="ACTIVE")
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    
    txn_id = str(uuid.uuid4())
    txn = Transaction(
        id=txn_id,
        amount=100.0,
        currency="USD",
        status="COMPLETED",
        transaction_type="TRANSFER",
        sender_account_id=acc_id
    )
    db_session.add(txn)
    db_session.commit()
    return txn

@pytest.fixture
def test_evaluation(db_session: Session, test_transaction):
    eval_id = str(uuid.uuid4())
    evaluation = RiskEvaluation(
        id=eval_id,
        transaction_id=test_transaction.id,
        score=0.8,
        category="HIGH_RISK",
        decision="BLOCK",
        policy_version="1.0",
        engine_version="1.0",
        explanation="Test explanation",
        correlation_id="corr-1"
    )
    db_session.add(evaluation)
    db_session.commit()
    db_session.refresh(evaluation)
    return evaluation

def get_auth_headers(user: User):
    from app.core.security import create_access_token
    token = create_access_token(user.id, roles=[r.name for r in user.roles])
    return {"Authorization": f"Bearer {token}"}

def test_risk_evolution(admin_user, test_evaluation, test_transaction):
    headers = get_auth_headers(admin_user)
    # The entity ID for the transaction sender
    entity_id = test_transaction.sender_account_id
    response = client.get(f"/api/v1/competition/evolution/{entity_id}?entity_type=ACCOUNT", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == entity_id
    assert data["risk_score"] == 0.8
    assert "delta_1h" in data

def test_detect_fraud_ring(admin_user, db_session):
    headers = get_auth_headers(admin_user)
    db_session.query(GraphEdge).delete()
    db_session.query(GraphNode).delete()
    db_session.commit()
    # Set up graph edges
    root_id = str(uuid.uuid4())
    root_node = GraphNode(id=root_id, node_type=f"ACCOUNT_{root_id}", entity_id=root_id)
    db_session.add(root_node)
    db_session.flush()
    
    for i in range(11):
        target_id = str(uuid.uuid4())
        target_node = GraphNode(id=target_id, node_type=f"ACCOUNT_{target_id}", entity_id=target_id)
        db_session.add(target_node)
        db_session.flush()
        
        edge = GraphEdge(
            id=str(uuid.uuid4()),
            source_node_id=root_id,
            target_node_id=target_id,
            relationship_type="TRANSFERRED_TO",
            weight=1.0
        )
        db_session.add(edge)
    db_session.commit()
    
    response = client.post(f"/api/v1/competition/fraud-ring/{root_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["signal_type"] == "FAN_OUT"

def test_replay_decision(admin_user, test_evaluation):
    headers = get_auth_headers(admin_user)
    response = client.post(f"/api/v1/competition/replay/{test_evaluation.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "replayed_score" in data
    assert "divergence" in data

def test_simulate_what_if(admin_user):
    headers = get_auth_headers(admin_user)
    payload = {
        "amount": 500.0,
        "currency": "USD",
        "transaction_type": "TRANSFER",
        "timestamp": datetime.now(UTC).isoformat(),
        "correlation_id": "test-sim-1"
    }
    response = client.post("/api/v1/competition/simulate/what-if", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "score" in data["results"]

def test_simulate_scenario(admin_user):
    headers = get_auth_headers(admin_user)
    response = client.post(
        "/api/v1/competition/simulate/scenario?scenario_name=test_scen", 
        json={"param1": "value1"}, 
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_scen"

def test_fuse_intelligence(admin_user):
    headers = get_auth_headers(admin_user)
    entity_id = "test-entity-1"
    payload = {"ip": "1.2.3.4", "risk": "high"}
    response = client.post(f"/api/v1/competition/fusion/{entity_id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == entity_id
    assert data["aggregated_context"] == payload

def test_add_feedback(admin_user):
    headers = get_auth_headers(admin_user)
    response = client.post(
        "/api/v1/competition/feedback?target_id=t1&target_type=ALERT&feedback_type=TRUE_POSITIVE&comments=test", 
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["feedback_type"] == "TRUE_POSITIVE"
    assert data["comments"] == "test"
