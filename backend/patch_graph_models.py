import re
with open("app/models/intelligence.py", "r") as f:
    content = f.read()

from sqlalchemy import UniqueConstraint, Integer, DateTime

graph_node_def = """
class GraphNode(Base, TimestampMixin):
    __tablename__ = "graph_nodes"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    node_type: Mapped[str] = mapped_column(String, index=True)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    __table_args__ = (
        UniqueConstraint('node_type', 'entity_id', name='uix_graph_node_type_entity'),
    )
"""

graph_edge_def = """
from sqlalchemy import Integer, DateTime
from datetime import datetime, UTC

class GraphEdge(Base, TimestampMixin):
    __tablename__ = "graph_edges"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id"))
    target_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id"))
    relationship_type: Mapped[str] = mapped_column(String, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    count: Mapped[int] = mapped_column(Integer, default=1)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    __table_args__ = (
        UniqueConstraint('source_node_id', 'target_node_id', 'relationship_type', name='uix_graph_edge'),
    )
"""

content = re.sub(r'class GraphNode\(.*?\n\n', graph_node_def + "\n", content, flags=re.DOTALL)
content = re.sub(r'class GraphEdge\(.*?\n\n', graph_edge_def + "\n", content, flags=re.DOTALL)

with open("app/models/intelligence.py", "w") as f:
    f.write(content)
