from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any

from app.schemas.fraud import FraudSignal
from app.schemas.risk import RiskSignalInput, RiskContext
from app.models.transaction import Transaction
from app.models.customer import Customer, Account
from app.models.intelligence import Rule, RuleVersion

class FraudContext:
    def __init__(self, db: Session, transaction_id: str):
        self.db = db
        self.transaction_id = transaction_id
        
        self.transaction = db.query(Transaction).filter_by(id=transaction_id).first()
        if not self.transaction:
            raise ValueError("Transaction not found")
            
        # Get sender account
        self.sender_account = db.query(Account).filter_by(id=self.transaction.sender_account_id).first()
        self.receiver_account = db.query(Account).filter_by(id=self.transaction.receiver_account_id).first()
        
        # We fetch recent transactions for velocity/behavior (e.g. last 24h)
        twenty_four_hours_ago = self.transaction.created_at - timedelta(hours=24)
        self.recent_transactions = db.query(Transaction).filter(
            Transaction.sender_account_id == self.sender_account.id,
            Transaction.created_at >= twenty_four_hours_ago,
            Transaction.id != self.transaction.id
        ).all()
        
class FraudFeatureExtractor:
    @staticmethod
    def extract(context: FraudContext) -> Dict[str, Any]:
        tx = context.transaction
        recent_txs = context.recent_transactions
        
        # Time windows
        now = tx.created_at
        txs_15m = [t for t in recent_txs if t.created_at >= now - timedelta(minutes=15)]
        txs_1h = [t for t in recent_txs if t.created_at >= now - timedelta(hours=1)]
        
        features = {
            "amount": tx.amount,
            "channel": tx.channel,
            "type": tx.transaction_type,
            "hour_of_day": now.hour,
            
            "count_15m": len(txs_15m),
            "amount_15m": sum(t.amount for t in txs_15m),
            "count_1h": len(txs_1h),
            "amount_1h": sum(t.amount for t in txs_1h),
            
            "unique_beneficiaries_24h": len(set(t.receiver_account_id for t in recent_txs))
        }
        
        # Baseline over 24h
        if recent_txs:
            amounts = sorted([t.amount for t in recent_txs])
            median_amount = amounts[len(amounts)//2]
            features["median_amount_24h"] = median_amount
        else:
            features["median_amount_24h"] = None
            
        return features

class VelocityProvider:
    @staticmethod
    def evaluate(context: FraudContext, features: Dict[str, Any]) -> List[FraudSignal]:
        signals = []
        count_15m = features.get("count_15m", 0)
        
        # Example deterministic logic: > 5 tx in 15m is high velocity
        if count_15m > 5:
            norm_value = min(count_15m / 10.0, 1.0) # Cap at 10
            signals.append(FraudSignal(
                signal_type="HIGH_TRANSACTION_VELOCITY",
                provider="VelocityProvider",
                raw_value=count_15m,
                normalized_value=norm_value,
                weight=0.8,
                confidence=0.9,
                reliability=0.95,
                severity="HIGH",
                evidence=f"{count_15m} transactions within 15 minutes",
                explanation="Transaction frequency significantly exceeds normal bounds.",
                provenance={"version": "1.0", "detector": "velocity"}
            ))
        return signals

class BehavioralProvider:
    @staticmethod
    def evaluate(context: FraudContext, features: Dict[str, Any]) -> List[FraudSignal]:
        signals = []
        median = features.get("median_amount_24h")
        amt = features.get("amount", 0)
        
        if median and median > 0:
            ratio = amt / median
            if ratio > 3.0:
                norm_value = min((ratio - 3.0) / 7.0, 1.0) # Caps at 10x
                signals.append(FraudSignal(
                    signal_type="AMOUNT_ANOMALY",
                    provider="BehavioralProvider",
                    raw_value=ratio,
                    normalized_value=norm_value,
                    weight=0.7,
                    confidence=0.85,
                    reliability=0.9,
                    severity="MEDIUM",
                    evidence=f"Transaction amount is {ratio:.1f}x the 24h median",
                    explanation="Amount significantly deviates from recent historical baseline.",
                    provenance={"version": "1.0", "detector": "behavioral"}
                ))
                
        # Channel anomaly
        recent_channels = set(t.channel for t in context.recent_transactions)
        if recent_channels and features.get("channel") not in recent_channels:
            signals.append(FraudSignal(
                signal_type="UNUSUAL_CHANNEL",
                provider="BehavioralProvider",
                raw_value=features.get("channel"),
                normalized_value=0.6,
                weight=0.5,
                confidence=0.8,
                reliability=0.9,
                severity="MEDIUM",
                evidence=f"Channel {features.get('channel')} not used in last 24h",
                explanation="Transaction originated from a rarely used channel.",
                provenance={"version": "1.0", "detector": "behavioral"}
            ))
            
        return signals

class ATOProvider:
    @staticmethod
    def evaluate(context: FraudContext, features: Dict[str, Any]) -> List[FraudSignal]:
        signals = []
        # ATO indicator: sudden channel change + amount anomaly + high velocity
        channel = features.get("channel")
        amt = features.get("amount", 0)
        median = features.get("median_amount_24h")
        
        recent_channels = set(t.channel for t in context.recent_transactions)
        is_new_channel = recent_channels and channel not in recent_channels
        is_high_amount = (median and median > 0 and (amt / median) > 3.0)
        is_high_vel = features.get("count_15m", 0) > 3
        
        if is_new_channel and is_high_amount and is_high_vel:
            signals.append(FraudSignal(
                signal_type="ACCOUNT_TAKEOVER_INDICATOR",
                provider="ATOProvider",
                raw_value="Multiple signals",
                normalized_value=0.9,
                weight=0.9,
                confidence=0.7, # Lower confidence as it's a heuristic
                reliability=0.8,
                severity="CRITICAL",
                evidence="New channel combined with high velocity and amount deviation",
                explanation="Pattern strongly suggests potential account takeover.",
                provenance={"version": "1.0", "detector": "ato"}
            ))
        return signals

class MuleProvider:
    @staticmethod
    def evaluate(context: FraudContext, features: Dict[str, Any]) -> List[FraudSignal]:
        signals = []
        # Mule indicator: High incoming volume then rapid outgoing
        # Simplification for outbound tx: Check if we have many unique beneficiaries and high volume
        unique_bens = features.get("unique_beneficiaries_24h", 0)
        if unique_bens > 5 and features.get("amount_1h", 0) > 5000:
            signals.append(FraudSignal(
                signal_type="MULE_ACCOUNT_INDICATOR",
                provider="MuleProvider",
                raw_value=unique_bens,
                normalized_value=0.8,
                weight=0.8,
                confidence=0.75,
                reliability=0.85,
                severity="HIGH",
                evidence=f"{unique_bens} distinct beneficiaries and high volume in short window",
                explanation="Pattern matches typical money mule behavior (rapid dispersion).",
                provenance={"version": "1.0", "detector": "mule"}
            ))
        return signals

class RuleProvider:
    @staticmethod
    def evaluate(db: Session, context: FraudContext, features: Dict[str, Any]) -> List[FraudSignal]:
        signals = []
        # Fetch active rules
        rules = db.query(RuleVersion).filter(RuleVersion.is_active == True).all()
        for rv in rules:
            config = rv.configuration
            # Simple rule engine support
            if config.get("type") == "threshold":
                feature_name = config.get("feature")
                threshold = config.get("value")
                operator = config.get("operator")
                
                val = features.get(feature_name)
                if val is not None:
                    triggered = False
                    if operator == ">" and val > threshold: triggered = True
                    elif operator == "<" and val < threshold: triggered = True
                    elif operator == "==" and val == threshold: triggered = True
                    
                    if triggered:
                        signals.append(FraudSignal(
                            signal_type=f"RULE_{rv.rule.name.upper()}",
                            provider="RuleProvider",
                            raw_value=val,
                            normalized_value=config.get("normalized_value", 0.8),
                            weight=config.get("weight", 0.5),
                            confidence=1.0,
                            reliability=1.0,
                            severity="HIGH",
                            evidence=f"Feature {feature_name} ({val}) triggered rule threshold ({operator} {threshold})",
                            explanation=f"Custom rule {rv.rule.name} matched.",
                            provenance={"version": str(rv.version), "rule_id": rv.rule_id}
                        ))
        return signals

class FraudSignalAdapter:
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

class FraudIntelligenceOrchestrator:
    @staticmethod
    def evaluate(db: Session, transaction_id: str, correlation_id: str) -> List[RiskSignalInput]:
        try:
            context = FraudContext(db, transaction_id)
            features = FraudFeatureExtractor.extract(context)
            
            signals = []
            signals.extend(VelocityProvider.evaluate(context, features))
            signals.extend(BehavioralProvider.evaluate(context, features))
            signals.extend(ATOProvider.evaluate(context, features))
            signals.extend(MuleProvider.evaluate(context, features))
            signals.extend(RuleProvider.evaluate(db, context, features))
            
            return FraudSignalAdapter.adapt(signals)
        except Exception as e:
            # Fallback isolation: if fraud intelligence completely fails, return empty signals 
            # so Risk Engine can gracefully degrade (Score 0)
            print(f"Fraud intelligence orchestrator failed: {e}")
            return []
