from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.identity import User
from app.services.copilot_service import CopilotService
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

router = APIRouter()

class CopilotChatRequest(BaseModel):
    question: str

class CitationResponse(BaseModel):
    source_type: str
    source_id: str
    excerpt: str
    relevance: float
    model_config = ConfigDict(from_attributes=True)

class CopilotChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    key_findings: List[str]
    uncertainties: List[str]
    evidence: List[CitationResponse]
    confidence: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

@router.post("/cases/{case_id}/chat", response_model=CopilotChatResponse)
def ask_copilot(
    case_id: str,
    request: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = CopilotService.ask_question(db, case_id, current_user.id, request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
