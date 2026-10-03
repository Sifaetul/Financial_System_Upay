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
    print("Added root node", root_id)
    db.commit()
    print("Committed root node")
except Exception as e:
    print("Error:", e)
