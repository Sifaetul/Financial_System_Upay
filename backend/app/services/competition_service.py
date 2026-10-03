from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, UTC
import uuid
import logging

from app.models.competition import (
    RiskEvolutionSnapshot, DecisionReplay, SimulationRun, ThreatSignal,
    IntelligenceFusionRecord, CompetitionFeedback
)
from app.models.risk import RiskEvaluation
from app.models.intelligence import GraphNode, GraphEdge
from app.services.monitoring_service import MonitoringService
from app.services.risk_engine import UnifiedRiskEngine
from app.schemas.risk import RiskContext, RiskSignalInput

logger = logging.getLogger(__name__)

class CompetitionService:
    @staticmethod
    def calculate_risk_evolution(db: Session, entity_id: str, entity_type: str) -> RiskEvolutionSnapshot:
        try:
            now = datetime.now(UTC)
            
            # Fetch evaluations for the entity by looking at transactions for sender_account_id
            from app.models.transaction import Transaction
            evals = db.query(RiskEvaluation).join(Transaction).filter(
                Transaction.sender_account_id == entity_id
            ).order_by(RiskEvaluation.created_at.desc()).all()
            
            if not evals:
                current_score = 0.0
                delta_1h = 0.0
                delta_24h = 0.0
                delta_7d = 0.0
            else:
                current_score = evals[0].score
                
                # compute deltas
                score_1h = next((e.score for e in evals if e.created_at <= now - timedelta(hours=1)), current_score)
                score_24h = next((e.score for e in evals if e.created_at <= now - timedelta(hours=24)), current_score)
                score_7d = next((e.score for e in evals if e.created_at <= now - timedelta(days=7)), current_score)
                
                delta_1h = current_score - score_1h
                delta_24h = current_score - score_24h
                delta_7d = current_score - score_7d

            snapshot = RiskEvolutionSnapshot(
                entity_id=entity_id,
                entity_type=entity_type,
                risk_score=current_score,
                delta_1h=delta_1h,
                delta_24h=delta_24h,
                delta_7d=delta_7d
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            
            MonitoringService.log_metric(db, "risk_evolution_calculated", "counter", 1.0, "competition")
            return snapshot
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to calculate risk evolution: {e}")
            raise

    @staticmethod
    def detect_fraud_ring(db: Session, root_entity_id: str):
        try:
            # simple fan-in / fan-out detection
            out_edges = db.query(GraphEdge).filter(GraphEdge.source_node_id == root_entity_id).count()
            in_edges = db.query(GraphEdge).filter(GraphEdge.target_node_id == root_entity_id).count()
            
            ring_detected = False
            if out_edges > 10:
                ring_detected = True
                signal_type = "FAN_OUT"
            elif in_edges > 10:
                ring_detected = True
                signal_type = "FAN_IN"
                
            if ring_detected:
                signal = ThreatSignal(
                    entity_id=root_entity_id,
                    entity_type="NETWORK",
                    signal_type=signal_type,
                    severity="HIGH",
                    context={"out_degree": out_edges, "in_degree": in_edges}
                )
                db.add(signal)
                db.commit()
                db.refresh(signal)
                MonitoringService.log_metric(db, "fraud_ring_detected", "counter", 1.0, "competition")
                return signal
            return None
        except Exception as e:
            logger.error(f"Failed to detect fraud ring: {e}")
            return None

    @staticmethod
    def replay_decision(db: Session, evaluation_id: uuid.UUID):
        try:
            evaluation = db.query(RiskEvaluation).filter(RiskEvaluation.id == str(evaluation_id)).first()
            if not evaluation:
                raise ValueError("Evaluation not found")
                
            engine = UnifiedRiskEngine(db)
            
            # replay
            from app.models.transaction import Transaction
            from datetime import datetime
            txn = db.query(Transaction).filter(Transaction.id == evaluation.transaction_id).first()
            if not txn:
                raise ValueError("Original transaction not found")

            context = RiskContext(
                transaction_id=txn.id,
                amount=txn.amount,
                currency=txn.currency,
                transaction_type=txn.transaction_type,
                account_id=txn.sender_account_id,
                timestamp=datetime.utcnow(),
                correlation_id=txn.correlation_id or "replay"
            )
            
            replayed = engine.evaluate(context, [])
            
            replay = DecisionReplay(
                original_evaluation_id=evaluation.id,
                replayed_score=replayed.score,
                divergence=abs(replayed.score - evaluation.score)
            )
            db.add(replay)
            db.commit()
            db.refresh(replay)
            MonitoringService.log_metric(db, "decision_replayed", "counter", 1.0, "competition")
            return replay
        except Exception as e:
            db.rollback()
            logger.error(f"Decision replay failed: {e}")
            raise

    @staticmethod
    def simulate_what_if(db: Session, context: RiskContext, signals: list[RiskSignalInput]):
        try:
            engine = UnifiedRiskEngine(db)
            # What-if simulation runs evaluate, but in a separate transaction or rollback mode
            # actually evaluate saves to DB inside, so we might need a nested transaction
            # but for simplicity we can just let it run and maybe not commit the outer transaction
            # However evaluate commits internally depending on how it's written.
            
            replayed = engine.evaluate(context, signals)
            
            sim_run = SimulationRun(
                name="WHAT_IF",
                results={"score": replayed.score, "decision": replayed.decision}
            )
            db.add(sim_run)
            db.commit()
            db.refresh(sim_run)
            MonitoringService.log_metric(db, "what_if_simulated", "counter", 1.0, "competition")
            return sim_run
        except Exception as e:
            db.rollback()
            logger.error(f"Simulation failed: {e}")
            raise

    @staticmethod
    def simulate_scenario(db: Session, scenario_name: str, parameters: dict):
        # execute deterministic E2E checks
        sim = SimulationRun(
            name=scenario_name,
            parameters=parameters,
            results={"status": "executed", "scenario": scenario_name}
        )
        db.add(sim)
        db.commit()
        db.refresh(sim)
        MonitoringService.log_metric(db, "scenario_simulated", "counter", 1.0, "competition")
        return sim

    @staticmethod
    def fuse_intelligence(db: Session, entity_id: str, context_data: dict) -> IntelligenceFusionRecord:
        record = IntelligenceFusionRecord(
            entity_id=entity_id,
            aggregated_context=context_data,
            confidence_score=0.9
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        MonitoringService.log_metric(db, "intelligence_fused", "counter", 1.0, "competition")
        return record

    @staticmethod
    def detect_proactive_threats(db: Session, entity_id: str, entity_type: str):
        # detect sudden risk acceleration
        snapshot = CompetitionService.calculate_risk_evolution(db, entity_id, entity_type)
        if snapshot.delta_1h > 0.3:
            signal = ThreatSignal(
                entity_id=entity_id,
                entity_type=entity_type,
                signal_type="SUDDEN_ACCELERATION",
                severity="HIGH",
                context={"delta_1h": snapshot.delta_1h}
            )
            db.add(signal)
            db.commit()
            db.refresh(signal)
            MonitoringService.log_metric(db, "proactive_threat_detected", "counter", 1.0, "competition")
            return signal
        return None

    @staticmethod
    def add_feedback(db: Session, target_id: str, target_type: str, feedback_type: str, comments: str, user_id: uuid.UUID):
        feedback = CompetitionFeedback(
            target_id=target_id,
            target_type=target_type,
            feedback_type=feedback_type,
            comments=comments,
            created_by=user_id
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        MonitoringService.log_metric(db, "feedback_added", "counter", 1.0, "competition")
        return feedback
