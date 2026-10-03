import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.intelligence import GraphNode, GraphEdge
from app.core.database import SessionLocal

db = SessionLocal()
try:
    root_id = str(uuid.uuid4())
    root_node = GraphNode(id=root_id, node_type=f"TEST_{root_id}", entity_id=root_id)
    db.add(root_node)
    
    for i in range(11):
        target_id = str(uuid.uuid4())
        target_node = GraphNode(id=target_id, node_type=f"TEST_{target_id}", entity_id=target_id)
        db.add(target_node)
        
        edge = GraphEdge(
            id=str(uuid.uuid4()),
            source_node_id=root_id,
            target_node_id=target_id,
            relationship_type="TRANSFERRED_TO",
            weight=1.0
        )
        db.add(edge)
    
    db.commit()
    print("Committed all nodes and edges")
except Exception as e:
    print("Error:", e)
