import networkx as nx
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional

from app.models.intelligence import GraphNode, GraphEdge
from app.models.transaction import Transaction
from app.models.customer import Account
from app.schemas.fraud import FraudSignal
from app.schemas.risk import RiskSignalInput

class GraphRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_node(self, node_type: str, entity_id: str) -> GraphNode:
        node = self.db.query(GraphNode).filter_by(node_type=node_type, entity_id=entity_id).first()
        if not node:
            node = GraphNode(node_type=node_type, entity_id=entity_id)
            self.db.add(node)
            self.db.flush()
        return node

    def upsert_edge(self, source_node: GraphNode, target_node: GraphNode, relationship_type: str, weight: float = 1.0):
        edge = self.db.query(GraphEdge).filter_by(
            source_node_id=source_node.id,
            target_node_id=target_node.id,
            relationship_type=relationship_type
        ).first()
        
        if edge:
            edge.weight += weight
            edge.count += 1
            edge.last_seen = datetime.now(UTC)
        else:
            edge = GraphEdge(
                source_node_id=source_node.id,
                target_node_id=target_node.id,
                relationship_type=relationship_type,
                weight=weight,
                count=1,
                first_seen=datetime.now(UTC),
                last_seen=datetime.now(UTC)
            )
            self.db.add(edge)
        self.db.flush()
        return edge

    def get_neighborhood(self, node_id: str, max_depth: int = 2) -> nx.DiGraph:
        """Extract a local subgraph around a node to limit query scope."""
        G = nx.DiGraph()
        
        # Iterative bounded BFS from database
        visited = set()
        queue = [(node_id, 0)]
        
        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)
            
            # Add node
            node = self.db.query(GraphNode).filter_by(id=current_id).first()
            if node:
                G.add_node(current_id, type=node.node_type, entity_id=node.entity_id)
            
            # Stop expanding at max depth
            if depth == max_depth:
                continue
                
            # Outbound edges
            out_edges = self.db.query(GraphEdge).filter_by(source_node_id=current_id).all()
            for e in out_edges:
                G.add_edge(e.source_node_id, e.target_node_id, type=e.relationship_type, weight=e.weight, count=e.count)
                if e.target_node_id not in visited:
                    queue.append((e.target_node_id, depth + 1))
            
            # Inbound edges
            in_edges = self.db.query(GraphEdge).filter_by(target_node_id=current_id).all()
            for e in in_edges:
                G.add_edge(e.source_node_id, e.target_node_id, type=e.relationship_type, weight=e.weight, count=e.count)
                if e.source_node_id not in visited:
                    queue.append((e.source_node_id, depth + 1))
                    
        return G

class GraphBuilder:
    @staticmethod
    def process_transaction(db: Session, transaction: Transaction):
        repo = GraphRepository(db)
        
        # Nodes
        tx_node = repo.get_or_create_node("TRANSACTION", transaction.id)
        sender_node = repo.get_or_create_node("ACCOUNT", transaction.sender_account_id)
        
        if transaction.receiver_account_id:
            receiver_node = repo.get_or_create_node("ACCOUNT", transaction.receiver_account_id)
            repo.upsert_edge(tx_node, receiver_node, "TRANSFERRED_TO")
            repo.upsert_edge(sender_node, receiver_node, "TRANSACTS_WITH", weight=transaction.amount)
        
        if transaction.channel:
            device_node = repo.get_or_create_node("DEVICE", transaction.channel) # simplistic device mapping
            repo.upsert_edge(sender_node, device_node, "USES_DEVICE")
            
        repo.upsert_edge(sender_node, tx_node, "INITIATED")

class GraphSignalService:
    @staticmethod
    def evaluate(db: Session, account_id: str) -> List[FraudSignal]:
        repo = GraphRepository(db)
        node = repo.get_or_create_node("ACCOUNT", account_id)
        G = repo.get_neighborhood(node.id, max_depth=2)
        
        signals = []
        
        # 1. Shared Device Intelligence
        device_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'DEVICE']
        for dn in device_nodes:
            # Accounts connected to this device
            connected_accounts = [u for u, v, d in G.in_edges(dn, data=True) if d.get('type') == 'USES_DEVICE']
            if len(connected_accounts) > 2:
                signals.append(FraudSignal(
                    signal_type="SHARED_DEVICE_CLUSTER",
                    provider="GraphIntelligence",
                    raw_value=len(connected_accounts),
                    normalized_value=min(len(connected_accounts) / 10.0, 1.0),
                    weight=0.8,
                    confidence=0.9,
                    reliability=0.95,
                    severity="HIGH",
                    evidence=f"Device shared among {len(connected_accounts)} distinct accounts",
                    explanation="Suspicious cluster detected: Multiple accounts sharing a single device.",
                    provenance={"detector_version": "1.0", "source": "GraphNetworkX"}
                ))
        
        # 2. Dense Counterparty Cluster
        # Using NetworkX to find high degree centralization for the account node
        if G.has_node(node.id):
            deg = G.degree(node.id)
            if deg > 10:
                signals.append(FraudSignal(
                    signal_type="HUB_ACCOUNT",
                    provider="GraphIntelligence",
                    raw_value=deg,
                    normalized_value=min(deg / 50.0, 1.0),
                    weight=0.6,
                    confidence=0.85,
                    reliability=0.9,
                    severity="MEDIUM",
                    evidence=f"Account has {deg} direct network connections",
                    explanation="High connectivity hub account detected.",
                    provenance={"detector_version": "1.0", "source": "GraphNetworkX"}
                ))
                
        return signals

class GraphRiskAdapter:
    @staticmethod
    def adapt(signals: List[FraudSignal]) -> List[RiskSignalInput]:
        return [
            RiskSignalInput(
                signal_id=f"{s.provider}_{s.signal_type}",
                signal_type=s.signal_type,
                source=s.provider,
                raw_value=s.raw_value,
                normalized_value=s.normalized_value,
                weight=s.weight,
                confidence=s.confidence,
                reliability=s.reliability,
                explanation=f"[{s.severity}] {s.explanation} Evidence: {s.evidence}",
                provenance=s.provenance
            )
            for s in signals
        ]
