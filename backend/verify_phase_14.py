import sys
import os
import uuid
import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.database import SessionLocal
from app.services.competition_service import CompetitionService
from app.models.transaction import Transaction
from app.schemas.risk import RiskContext
from app.models.intelligence import GraphNode, GraphEdge
from app.services.risk_engine import UnifiedRiskEngine
from sqlalchemy import func

def test_phase_14():
    db = SessionLocal()
    print("=== STARTING PHASE 14 ADVANCED VERIFICATION ===")
    
    tx = db.query(Transaction).first()
    if not tx:
        print("NO TRANSACTION FOUND")
        return
        
    node_root = GraphNode(id=str(uuid.uuid4()), node_type="ACCOUNT", entity_id="ROOT_ACC_" + str(uuid.uuid4())[:8])
    nodes = [node_root]
    edges = []
    
    for _ in range(12):
        n = GraphNode(id=str(uuid.uuid4()), node_type="ACCOUNT", entity_id="DEST_" + str(uuid.uuid4())[:8])
        nodes.append(n)
        edges.append(GraphEdge(id=str(uuid.uuid4()), source_node_id=node_root.id, target_node_id=n.id, relationship_type="TRANSFERRED_TO", weight=1.0))
        
    db.add_all(nodes)
    db.commit()
    db.add_all(edges)
    db.commit()
    
    network_result = CompetitionService.detect_fraud_ring(db, node_root.id)
    if network_result:
        print(f"Network Intelligence ID: {network_result.id}, Severity: {network_result.severity}, Signal: {network_result.signal_type}")
    else:
        print("Network Intelligence: NONE DETECTED (Logic might be empty)")
        
if __name__ == "__main__":
    test_phase_14()
