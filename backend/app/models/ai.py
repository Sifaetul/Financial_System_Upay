from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from pgvector.sqlalchemy import Vector
from .base import Base, TimestampMixin, generate_uuid
from typing import List

class AiDocument(Base, TimestampMixin):
    __tablename__ = "ai_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String, nullable=True)
    source_type: Mapped[str] = mapped_column(String, index=True, nullable=True) 
    source_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    entity_type: Mapped[str] = mapped_column(String, nullable=True)
    entity_id: Mapped[str] = mapped_column(String, nullable=True)
    case_id: Mapped[str] = mapped_column(String, ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=True)
    access_scope: Mapped[str] = mapped_column(String, nullable=True)
    
    chunks: Mapped[List["AiChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")

class AiChunk(Base, TimestampMixin):
    __tablename__ = "ai_chunks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("ai_documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column(String)
    
    embedding = mapped_column(Vector(384))
    
    document: Mapped["AiDocument"] = relationship(back_populates="chunks")
