import time
from app.services.monitoring_service import MonitoringService
from sqlalchemy.orm import Session
from app.models.risk import RiskEvaluation, RiskEvaluationSignal
from app.schemas.risk import RiskContext, RiskSignalInput, RiskEvaluationResult
from app.models.event import OutboxEvent
from app.models.intelligence import FeatureSnapshot
import uuid
import datetime

class RiskDecisionPolicy:
    def __init__(self, version: str):
        self.version = version

    def map_score_to_category(self, score: float) -> str:
        if score >= 0.85: return "CRITICAL"
        if score >= 0.65: return "HIGH"
        if score >= 0.35: return "MEDIUM"
        if score >= 0.15: return "LOW"
        return "VERY_LOW"
        
    def map_category_to_decision(self, category: str) -> str:
        mapping = {
            "CRITICAL": "BLOCK",
            "HIGH": "STEP_UP",
            "MEDIUM": "REVIEW",
            "LOW": "ALLOW",
            "VERY_LOW": "ALLOW"
        }
        return mapping.get(category, "REVIEW")

class UnifiedRiskEngine:
    ENGINE_VERSION = "1.0.0"

    def __init__(self, db: Session):
        self.db = db
        self.policy = RiskDecisionPolicy(version="policy-v1.0")

    def evaluate(self, context: RiskContext, signals: list[RiskSignalInput]) -> RiskEvaluation:
        start_t = time.time()
        # 1. Quality Assessment & Weighted Risk Fusion
        total_effective_weight = 0.0
        weighted_score_sum = 0.0
        overall_confidence = 0.0
        
        signal_contributions = []
        
        for sig in signals:
            effective_weight = sig.weight * sig.confidence * sig.reliability
            total_effective_weight += effective_weight
            
            contribution = sig.normalized_value * effective_weight
            weighted_score_sum += contribution
            overall_confidence += (sig.confidence * sig.weight)
            
            signal_contributions.append({
                "signal": sig,
                "effective_weight": effective_weight,
                "contribution": contribution
            })
            
        if total_effective_weight > 0:
            final_score = weighted_score_sum / total_effective_weight
            confidence_summary = overall_confidence / sum([s.weight for s in signals]) if signals else 1.0
        else:
            final_score = 0.0
            confidence_summary = 1.0
            
        # Ensure bounds
        final_score = min(max(final_score, 0.0), 1.0)
        
        # 2. Risk Category & Decision Policy
        category = self.policy.map_score_to_category(final_score)
        decision = self.policy.map_category_to_decision(category)
        
        # 3. Explainable Decision
        # Sort contributors by contribution descending
        sorted_contributions = sorted(signal_contributions, key=lambda x: x["contribution"], reverse=True)
        top_signals = sorted_contributions[:3]
        
        explanation_lines = [f"Risk increased primarily because of:"]
        for c in top_signals:
            if c["contribution"] > 0:
                explanation_lines.append(f"- {c['signal'].signal_type}: {c['signal'].explanation} (contrib: {c['contribution']:.3f})")
                
        explanation = "\n".join(explanation_lines) if final_score > 0 else "Risk is minimal based on available signals."

        # 4. Persistence
        evaluation = RiskEvaluation(
            transaction_id=context.transaction_id,
            event_id=context.event_id,
            score=final_score,
            category=category,
            decision=decision,
            policy_version=self.policy.version,
            engine_version=self.ENGINE_VERSION,
            confidence_summary=confidence_summary,
            explanation=explanation,
            correlation_id=context.correlation_id,
            causation_id=context.causation_id
        )
        evaluation.id = str(uuid.uuid4())
        self.db.add(evaluation)
        self.db.flush() # get ID
        
        for c in signal_contributions:
            sig = c["signal"]
            eval_sig = RiskEvaluationSignal(
                evaluation_id=evaluation.id,
                signal_id=sig.signal_id,
                signal_type=sig.signal_type,
                source=sig.source,
                raw_value=str(sig.raw_value),
                normalized_value=sig.normalized_value,
                weight=sig.weight,
                confidence=sig.confidence,
                reliability=sig.reliability,
                contribution=c["contribution"],
                explanation=sig.explanation,
                provenance=sig.provenance
            )
            self.db.add(eval_sig)
            
        
        # Feature Snapshot Persistence
        snapshot = FeatureSnapshot(
            entity_id=evaluation.id,
            features=context.model_dump(mode="json")
        )
        self.db.add(snapshot)
        
        # Publish Risk Evaluation Event via Outbox

        outbox = OutboxEvent(
            event_type="risk.evaluation.completed",
            schema_version=1,
            aggregate_type="RiskEvaluation",
            aggregate_id=evaluation.id,
            correlation_id=context.correlation_id,
            causation_id=evaluation.id,
            payload={
                "score": final_score,
                "category": category,
                "decision": decision,
                "transaction_id": context.transaction_id
            }
        )
        self.db.add(outbox)
        self.db.commit()
        self.db.refresh(evaluation)
                
        latency_ms = (time.time() - start_t) * 1000
        MonitoringService.log_metric(self.db, "risk_evaluation_latency_ms", "HISTOGRAM", latency_ms, "unified_risk_engine")
        MonitoringService.log_metric(self.db, "risk_evaluations_total", "COUNTER", 1.0, "unified_risk_engine")
        MonitoringService.log_metric(self.db, f"risk_decision_{evaluation.decision}", "COUNTER", 1.0, "unified_risk_engine")
        
        return evaluation


class RiskSignalCollector:
    def __init__(self):
        self.providers = []
        
    def register_provider(self, provider_func):
        self.providers.append(provider_func)
        
    def collect(self, context: RiskContext) -> list[RiskSignalInput]:
        signals = []
        for provider in self.providers:
            try:
                sig = provider(context)
                if sig:
                    if isinstance(sig, list):
                        signals.extend(sig)
                    else:
                        signals.append(sig)
            except Exception as e:
                # Fallback: Degradation
                print(f"Provider failed: {e}")
                # We could inject a degraded signal or just skip
        return signals

# Dummy providers for demonstration
def amount_velocity_provider(context: RiskContext) -> list[RiskSignalInput]:
    # In a real system, this would query DB for velocity
    # Here we mock a deterministic rule
    normalized = min(context.amount / 10000.0, 1.0)
    return [
        RiskSignalInput(
            signal_id=f"vel_{context.transaction_id}",
            signal_type="velocity_deviation",
            source="amount_velocity_provider",
            raw_value=context.amount,
            normalized_value=normalized,
            weight=0.8,
            confidence=0.9,
            reliability=0.95,
            explanation=f"Amount {context.amount} evaluated for velocity deviation",
            provenance={"version": "1.0", "rule": "velocity_check"}
        )
    ]

def location_anomaly_provider(context: RiskContext) -> RiskSignalInput:
    # Another dummy deterministic provider
    # E.g., assume high risk if channel is "API_UNKNOWN"
    norm = 0.8 if context.channel == "API_UNKNOWN" else 0.1
    return RiskSignalInput(
        signal_id=f"loc_{context.transaction_id}",
        signal_type="location_anomaly",
        source="location_anomaly_provider",
        raw_value=context.channel,
        normalized_value=norm,
        weight=0.6,
        confidence=0.8,
        reliability=0.85,
        explanation=f"Channel {context.channel} evaluated for location anomaly",
        provenance={"version": "1.0", "rule": "location_check"}
    )
