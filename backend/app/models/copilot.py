from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, JSON, ForeignKey, DateTime, Float
from typing import List
from datetime import datetime, UTC
from .base import Base, TimestampMixin, generate_uuid

class CopilotConversation(Base, TimestampMixin):
    __tablename__ = "copilot_conversations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String, ForeignKey("investigation_cases.id", ondelete="CASCADE"))
    investigator_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    
    messages: Mapped[List["CopilotMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")

class CopilotMessage(Base, TimestampMixin):
    __tablename__ = "copilot_messages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("copilot_conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String) # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(String)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    feedback: Mapped[str] = mapped_column(String, nullable=True)
    
    conversation: Mapped["CopilotConversation"] = relationship(back_populates="messages")
    citations: Mapped[List["CopilotCitation"]] = relationship(back_populates="message", cascade="all, delete-orphan")

class CopilotCitation(Base):
    __tablename__ = "copilot_citations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    message_id: Mapped[str] = mapped_column(String, ForeignKey("copilot_messages.id", ondelete="CASCADE"))
    source_type: Mapped[str] = mapped_column(String)
    source_id: Mapped[str] = mapped_column(String)
    excerpt: Mapped[str] = mapped_column(String)
    relevance: Mapped[float] = mapped_column(Float, nullable=True)
    
    message: Mapped["CopilotMessage"] = relationship(back_populates="citations")
