from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_permissions
from app.models.intelligence import GraphNode, GraphEdge
from app.services.graph_intelligence import GraphRepository
from typing import List, Dict, Any

router = APIRouter()

@router.get("/neighborhood/{node_type}/{node_id}")
def get_neighborhood(
    node_type: str,
    node_id: str,
    depth: int = 2,
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    if depth > 3:
        raise HTTPException(status_code=400, detail="Max traversal depth is 3")
        
    repo = GraphRepository(db)
    root = db.query(GraphNode).filter_by(node_type=node_type, entity_id=node_id).first()
    if not root:
        raise HTTPException(status_code=404, detail="Node not found")
        
    G = repo.get_neighborhood(root.id, max_depth=depth)
    
    nodes = [{"id": n, "type": d.get("type"), "entity_id": d.get("entity_id")} for n, d in G.nodes(data=True)]
    edges = [{"source": u, "target": v, "type": d.get("type"), "weight": d.get("weight"), "count": d.get("count")} for u, v, d in G.edges(data=True)]
    
    return {"nodes": nodes, "edges": edges}

@router.get("/signals/{node_type}/{node_id}")
def get_graph_signals(
    node_type: str,
    node_id: str,
    db: Session = Depends(get_db),
    _ = Depends(require_permissions(["manage_transactions"]))
):
    if node_type != "ACCOUNT":
        raise HTTPException(status_code=400, detail="Signals only supported for ACCOUNT nodes currently")
        
    from app.services.graph_intelligence import GraphSignalService
    signals = GraphSignalService.evaluate(db, node_id)
    return {"signals": [s.model_dump() for s in signals]}
