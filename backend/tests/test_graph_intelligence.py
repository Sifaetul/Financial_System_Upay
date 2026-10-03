import pytest
from app.core.database import SessionLocal
from app.models.customer import Customer, Account
from app.models.transaction import Transaction
from app.services.graph_intelligence import GraphRepository, GraphBuilder, GraphSignalService
import uuid

def test_graph_upsert_idempotency():
    db = SessionLocal()
    repo = GraphRepository(db)
    
    n1 = repo.get_or_create_node("ACCOUNT", "A1")
    n2 = repo.get_or_create_node("DEVICE", "D1")
    
    # Upsert edge once
    e1 = repo.upsert_edge(n1, n2, "USES_DEVICE", weight=1.0)
    assert e1.count == 1
    
    # Upsert same edge again
    e2 = repo.upsert_edge(n1, n2, "USES_DEVICE", weight=1.0)
    
    # Should be the same edge record, count increased
    assert e1.id == e2.id
    assert e2.count == 2
    assert e2.weight == 2.0
    
    db.close()

def test_shared_device_signal():
    db = SessionLocal()
    repo = GraphRepository(db)
    
    # Create 3 accounts sharing 1 device
    d1 = repo.get_or_create_node("DEVICE", "TEST_DEVICE_X")
    a1 = repo.get_or_create_node("ACCOUNT", "ACC_1")
    a2 = repo.get_or_create_node("ACCOUNT", "ACC_2")
    a3 = repo.get_or_create_node("ACCOUNT", "ACC_3")
    
    repo.upsert_edge(a1, d1, "USES_DEVICE")
    repo.upsert_edge(a2, d1, "USES_DEVICE")
    repo.upsert_edge(a3, d1, "USES_DEVICE")
    db.commit()
    
    signals = GraphSignalService.evaluate(db, "ACC_1")
    assert any(s.signal_type == "SHARED_DEVICE_CLUSTER" for s in signals)
    
    db.close()

def test_hub_account_signal():
    db = SessionLocal()
    repo = GraphRepository(db)
    
    # Create 1 account transacting with 11 others
    hub = repo.get_or_create_node("ACCOUNT", "HUB_ACC")
    
    for i in range(11):
        peer = repo.get_or_create_node("ACCOUNT", f"PEER_{i}")
        repo.upsert_edge(hub, peer, "TRANSFERRED_TO")
        
    db.commit()
    
    signals = GraphSignalService.evaluate(db, "HUB_ACC")
    assert any(s.signal_type == "HUB_ACCOUNT" for s in signals)
    
    db.close()
    
def test_graph_builder_transaction():
    db = SessionLocal()
    tx_id = str(uuid.uuid4())
    tx = Transaction(
        id=tx_id, 
        amount=100.0, 
        currency="USD", 
        transaction_type="SEND_MONEY", 
        sender_account_id="ACC_A", 
        receiver_account_id="ACC_B", 
        channel="MOBILE_APP", 
        status="RECEIVED", 
        idempotency_key=str(uuid.uuid4())
    )
    
    # Process without committing tx to DB (GraphBuilder shouldn't care if tx is persisted or not, it only reads properties)
    GraphBuilder.process_transaction(db, tx)
    db.commit()
    
    repo = GraphRepository(db)
    n = repo.get_or_create_node("ACCOUNT", "ACC_A")
    G = repo.get_neighborhood(n.id)
    
    assert len(G.nodes) > 1 # ACC_A, ACC_B, DEVICE, TX
    db.close()
