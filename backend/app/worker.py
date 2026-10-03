from app.models.transaction import TransactionEvent
from app.models.customer import Account
from celery import Celery
from app.core.config import settings
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.event import OutboxEvent, ProcessedEvent, DeadLetterEvent
from app.models.transaction import Transaction

from app.schemas.risk import RiskContext
from app.services.risk_engine import UnifiedRiskEngine
from app.services.fraud_intelligence import FraudIntelligenceOrchestrator
from app.services.graph_intelligence import GraphBuilder, GraphSignalService, GraphRiskAdapter
from app.services.customer_intelligence import CustomerProfileService, CustomerBehaviorService, CustomerSignalAdapter
from app.services.financial_intelligence import FinancialProfileService, FinancialBehaviorService, FinancialSignalAdapter
from app.services.merchant_intelligence import MerchantProfileService, MerchantBehaviorService, MerchantSignalAdapter
from app.services.agent_intelligence import AgentProfileService, AgentBehaviorService, AgentSignalAdapter
from app.models.transaction import Transaction
from app.models.customer import Account
import uuid
from datetime import datetime, UTC

import traceback

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URI,
    backend=settings.REDIS_URI
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1
)

@celery_app.task(name="outbox_publisher")
def outbox_publisher():
    db = SessionLocal()
    try:
        events = db.query(OutboxEvent).filter(OutboxEvent.status == "PENDING").limit(50).all()
        for event in events:
            # Publish to actual consumer tasks
            if event.event_type.startswith("transaction."):
                process_transaction_event.delay(event.id, event.event_type, event.payload, event.correlation_id, event.causation_id, event.aggregate_id)
            
            event.status = "PUBLISHED"
        db.commit()
    finally:
        db.close()


@celery_app.task(name="process_transaction_event", bind=True, max_retries=3)
def process_transaction_event(self, event_id: str, event_type: str, payload: dict, correlation_id: str, causation_id: str, aggregate_id: str):
    db = SessionLocal()
    consumer_name = "transaction_event_processor"
    
    try:
        # Check idempotency
        processed = db.query(ProcessedEvent).filter_by(event_id=event_id, consumer_name=consumer_name).first()
        if processed:
            return "Already processed"

        # Record domain event persistently in Phase 2's structure
        if "transaction." in event_type:
            # payload must contain status for our simple processor
            tx_id = aggregate_id
            tx_event = TransactionEvent(transaction_id=tx_id, event_type=event_type, schema_version=1, correlation_id=correlation_id, causation_id=event_id, payload=payload)
            db.add(tx_event) # Outbox usually puts aggregate_id at root, but we can fall back
            
            
            # Build Graph, Customer, Financial, Merchant and Agent Profiles
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)
                    CustomerProfileService.process_transaction(db, tx)
                    FinancialProfileService.process_transaction(db, tx)
                    MerchantProfileService.process_transaction(db, tx)
                    AgentProfileService.process_transaction(db, tx)
            
            # Risk evaluation moved to end
                
            # Just store the Domain Event for audit

            pass # We don't have tx_id readily here unless passed. Wait, aggregate_id was in outbox but we didn't pass it to task!
            # It's fine, this is just a dummy consumer to prove the architecture.
            pass
            
        # Mark processed
        db.add(ProcessedEvent(event_id=event_id, consumer_name=consumer_name))
        db.commit()
        
        # Trigger Async Risk Evaluation after commit to avoid deadlock in eager mode
        if event_type == "transaction.received":
            process_risk_evaluation.delay(event_id, tx_id, payload, correlation_id)

    except Exception as exc:
        db.rollback()
        # Handle DLQ on max retries
        if self.request.retries == self.max_retries:
            db.add(DeadLetterEvent(
                event_id=event_id, 
                event_type=event_type, 
                consumer_name=consumer_name, 
                failure_reason=str(exc),
                payload=payload
            ))
            db.commit()
            return "Sent to DLQ"
        else:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        db.close()



@celery_app.task(name="process_risk_evaluation", bind=True, max_retries=3)
def process_risk_evaluation(self, event_id: str, transaction_id: str, payload: dict, correlation_id: str):
    db = SessionLocal()
    consumer_name = "risk_event_processor"
    try:
        # Check idempotency
        processed = db.query(ProcessedEvent).filter_by(event_id=event_id, consumer_name=consumer_name).first()
        if processed:
            return "Already processed"
            
        # Build context
        context = RiskContext(
            transaction_id=transaction_id,
            event_id=event_id,
            amount=payload.get("amount", 0.0),
            currency=payload.get("currency", "USD"),
            transaction_type=payload.get("transaction_type", "UNKNOWN"),
            channel=payload.get("channel", "WEB"),
            timestamp=datetime.now(UTC),
            correlation_id=correlation_id,
            causation_id=event_id
        )
        
        signals = FraudIntelligenceOrchestrator.evaluate(db, transaction_id, correlation_id)
        
        # Merge Graph and Customer Signals
        tx = db.query(Transaction).filter_by(id=transaction_id).first()
        if tx:
            graph_fraud_signals = GraphSignalService.evaluate(db, tx.sender_account_id)
            signals.extend(GraphRiskAdapter.adapt(graph_fraud_signals))
            
            sender_account = db.query(Account).filter_by(id=tx.sender_account_id).first()
            if sender_account:
                customer_signals = CustomerBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(CustomerSignalAdapter.adapt(customer_signals))
                
                financial_signals = FinancialBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(FinancialSignalAdapter.adapt(financial_signals))
            
            # Merchant Signals (If applicable)
            if tx.merchant_id:
                merchant_signals = MerchantBehaviorService.evaluate(db, tx.merchant_id)
                signals.extend(MerchantSignalAdapter.adapt(merchant_signals))
                
            # Agent Signals (If applicable)
            if tx.agent_id:
                agent_signals = AgentBehaviorService.evaluate(db, tx.agent_id)
                signals.extend(AgentSignalAdapter.adapt(agent_signals))
        
        engine = UnifiedRiskEngine(db)
        engine.evaluate(context, signals)
        
        # Mark processed
        db.add(ProcessedEvent(event_id=event_id, consumer_name=consumer_name))
        db.commit()
        


        
    except Exception as exc:
        db.rollback()
        # Handle DLQ on max retries
        if self.request.retries == self.max_retries:
            db.add(DeadLetterEvent(
                event_id=event_id, 
                event_type="risk_evaluation", 
                consumer_name=consumer_name, 
                failure_reason=str(exc),
                payload=payload
            ))
            db.commit()
            return "Sent to DLQ"
        else:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        db.close()
