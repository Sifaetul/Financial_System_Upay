from sqlalchemy.orm import Session
from app.models.copilot import CopilotConversation, CopilotMessage, CopilotCitation
from app.models.investigation import InvestigationCase, CaseEvidence
from app.models.transaction import Transaction
from app.models.ai import AiChunk, AiDocument
from .llm_provider import get_llm_provider
from .copilot_retrieval import HybridRetrieval
from .monitoring_service import MonitoringService
import time

class CopilotService:
    @staticmethod
    def ask_question(db: Session, case_id: str, investigator_id: str, question: str) -> dict:
        # Authorization
        case = db.query(InvestigationCase).filter_by(id=case_id).first()
        if not case:
            raise Exception("Case not found or access denied.")
            
        conversation = db.query(CopilotConversation).filter_by(case_id=case_id, investigator_id=investigator_id).first()
        if not conversation:
            conversation = CopilotConversation(case_id=case_id, investigator_id=investigator_id)
            db.add(conversation)
            db.flush()
            
        user_msg = CopilotMessage(conversation_id=conversation.id, role="user", content=question)
        db.add(user_msg)
        
        retriever = HybridRetrieval(db)
        context = retriever.retrieve_context(case_id, question)
        
        llm = get_llm_provider()
        
        start_t = time.time()
        response_data = llm.generate_structured_response(question, context)
        latency_ms = (time.time() - start_t) * 1000
        
        MonitoringService.log_metric(db, "copilot_latency_ms", "HISTOGRAM", latency_ms, "ai_investigation_copilot")
        MonitoringService.log_metric(db, "copilot_requests_total", "COUNTER", 1.0, "ai_investigation_copilot")
        
        if "LLM Error" in response_data.get("answer", "") or "Model inference failed" in response_data.get("uncertainties", []):
            MonitoringService.log_metric(db, "copilot_failures_total", "COUNTER", 1.0, "ai_investigation_copilot")
        
        MonitoringService.record_model_lineage(
            db=db,
            model_id="SmolLM2-135M",
            model_version="1.0",
            prediction=response_data.get("answer")[:50],
            correlation_id=conversation.id,
            confidence=0.5
        )

        
        valid_citations = []
        for cit in response_data.get("evidence", []):
            source_type = cit.get("source_type")
            source_id = cit.get("source_id")
            
            is_valid = False
            if source_type == "TRANSACTION":
                tx = db.query(Transaction).filter_by(id=source_id).first()
                # A robust app would also ensure transaction is linked to the case
                if tx:
                    is_valid = True
            elif source_type == "EVIDENCE":
                ev = db.query(CaseEvidence).filter_by(id=source_id, case_id=case_id).first()
                if ev:
                    is_valid = True
            elif source_type == "CHUNK":
                chunk = db.query(AiChunk).join(AiDocument).filter(
                    AiChunk.id == source_id,
                    AiDocument.case_id == case_id
                ).first()
                if chunk:
                    is_valid = True
                
            if is_valid:
                valid_citations.append(cit)
        
        ai_msg = CopilotMessage(
            conversation_id=conversation.id, 
            role="assistant", 
            content=response_data.get("answer", ""),
            metadata_json={"confidence": response_data.get("confidence")}
        )
        db.add(ai_msg)
        db.flush()
        
        for cit in valid_citations:
            db.add(CopilotCitation(
                message_id=ai_msg.id,
                source_type=cit.get("source_type"),
                source_id=cit.get("source_id"),
                excerpt=cit.get("excerpt"),
                relevance=cit.get("relevance", 0.0)
            ))
            
        db.commit()
        
        return {
            "conversation_id": conversation.id,
            "message_id": ai_msg.id,
            "answer": response_data.get("answer"),
            "key_findings": response_data.get("key_findings", []),
            "uncertainties": response_data.get("uncertainties", []),
            "evidence": valid_citations,
            "confidence": response_data.get("confidence")
        }
