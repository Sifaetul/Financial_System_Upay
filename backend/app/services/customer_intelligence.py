from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any

from app.models.customer import Customer, CustomerProfile, CustomerSegment, Account
from app.models.transaction import Transaction
from app.schemas.fraud import FraudSignal
from app.schemas.risk import RiskSignalInput

class CustomerProfileService:
    @staticmethod
    def process_transaction(db: Session, transaction: Transaction):
        """Update customer profile metrics based on a new transaction."""
        sender_account = db.query(Account).filter_by(id=transaction.sender_account_id).first()
        if not sender_account:
            return
            
        customer_id = sender_account.customer_id
        profile = db.query(CustomerProfile).filter_by(customer_id=customer_id).first()
        
        if not profile:
            profile = CustomerProfile(customer_id=customer_id)
            db.add(profile)
            db.flush()
            
        # Time constraints
        now = datetime.now(UTC)
        if not profile.first_activity_at:
            profile.first_activity_at = now
        profile.last_activity_at = now
        
        # Calculate updated metrics safely for idempotency we can just query history
        txs = db.query(Transaction).join(Account, Transaction.sender_account_id == Account.id).filter(Account.customer_id == customer_id).all()
        
        profile.transaction_count = len(txs)
        profile.transaction_volume = sum(t.amount for t in txs)
        profile.average_transaction_amount = profile.transaction_volume / profile.transaction_count if profile.transaction_count > 0 else 0
        
        # Unique Beneficiaries
        receivers = {t.receiver_account_id for t in txs if t.receiver_account_id}
        profile.unique_beneficiary_count = len(receivers)
        
        # Unique Devices (Channel proxy)
        devices = {t.channel for t in txs if t.channel}
        profile.unique_device_count = len(devices)
        
        # Active Days
        active_days = {t.created_at.date() for t in txs if t.created_at}
        profile.active_days = len(active_days)
        
        profile.profile_version += 1
        db.flush()

        # Update Lifecycle and Segments
        CustomerLifecycleService.evaluate(db, profile)
        CustomerSegmentationService.evaluate(db, profile)

class CustomerBehaviorService:
    @staticmethod
    def evaluate(db: Session, customer_id: str) -> List[FraudSignal]:
        """Detect behavior changes comparing 7d vs 30d baseline."""
        signals = []
        now = datetime.now(UTC)
        
        txs = db.query(Transaction).join(Account, Transaction.sender_account_id == Account.id).filter(Account.customer_id == customer_id).all()
        
        txs_30d = [t for t in txs if t.created_at and t.created_at >= now - timedelta(days=30)]
        txs_7d = [t for t in txs_30d if t.created_at >= now - timedelta(days=7)]
        txs_historical = [t for t in txs_30d if t.created_at < now - timedelta(days=7)]
        
        if len(txs_historical) < 3:
            return signals # INSUFFICIENT_HISTORY
            
        avg_hist = sum(t.amount for t in txs_historical) / len(txs_historical) if txs_historical else 0
        avg_7d = sum(t.amount for t in txs_7d) / len(txs_7d) if txs_7d else 0
        
        if avg_hist > 0 and avg_7d > avg_hist * 3.0:
            signals.append(FraudSignal(
                signal_type="CUSTOMER_BEHAVIOR_CHANGE",
                provider="CustomerIntelligence",
                raw_value=avg_7d,
                normalized_value=min(avg_7d / (avg_hist * 5.0), 1.0),
                weight=0.9,
                confidence=0.85,
                reliability=0.9,
                severity="HIGH",
                evidence=f"Recent 7-day avg volume ({avg_7d:.2f}) is >3x the 30-day baseline ({avg_hist:.2f})",
                explanation="Significant customer behavior change detected.",
                provenance={"detector_version": "1.0", "source": "CustomerBehaviorDetector"}
            ))
            
        profile = db.query(CustomerProfile).filter_by(customer_id=customer_id).first()
        if profile and signals:
            profile.behavioral_stability = "HIGHLY_CHANGING"
        elif profile:
            profile.behavioral_stability = "STABLE"
            
        return signals

class CustomerLifecycleService:
    @staticmethod
    def evaluate(db: Session, profile: CustomerProfile):
        """Evaluate and transition lifecycle state."""
        now = datetime.now(UTC)
        if not profile.last_activity_at:
            return
            
        days_since_active = (now - profile.last_activity_at).days
        
        if profile.transaction_count == 1:
            profile.lifecycle_state = "NEW"
        elif days_since_active > 90:
            profile.lifecycle_state = "DORMANT"
        elif days_since_active > 30:
            profile.lifecycle_state = "INACTIVE"
        elif profile.lifecycle_state == "DORMANT" and days_since_active <= 7:
            profile.lifecycle_state = "REACTIVATED"
        else:
            profile.lifecycle_state = "ACTIVE"

class CustomerSegmentationService:
    @staticmethod
    def evaluate(db: Session, profile: CustomerProfile):
        """Evaluate customer segments based on profile metrics."""
        segment_name = "NEW"
        evidence = "Customer is new"
        
        if profile.transaction_count > 50 and profile.transaction_volume > 10000:
            segment_name = "HIGH_VALUE"
            evidence = f"Tx count: {profile.transaction_count}, Vol: {profile.transaction_volume}"
        elif profile.transaction_count > 20:
            segment_name = "HIGH_ACTIVITY"
            evidence = f"Tx count: {profile.transaction_count}"
        elif profile.transaction_count > 5:
            segment_name = "REGULAR"
            evidence = f"Tx count: {profile.transaction_count}"
        elif profile.transaction_count > 1:
            segment_name = "LOW_ACTIVITY"
            evidence = f"Tx count: {profile.transaction_count}"
            
        # Idempotent segment persistence
        segment = db.query(CustomerSegment).filter_by(customer_id=profile.customer_id, segment_name=segment_name).first()
        if not segment:
            # Delete old segments
            db.query(CustomerSegment).filter_by(customer_id=profile.customer_id).delete()
            segment = CustomerSegment(
                customer_id=profile.customer_id,
                segment_name=segment_name,
                evidence=evidence
            )
            db.add(segment)

class CustomerSignalAdapter:
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

class Customer360Service:
    @staticmethod
    def get_profile(db: Session, customer_id: str) -> Dict[str, Any]:
        customer = db.query(Customer).filter_by(id=customer_id).first()
        profile = db.query(CustomerProfile).filter_by(customer_id=customer_id).first()
        segment = db.query(CustomerSegment).filter_by(customer_id=customer_id).first()
        
        if not customer:
            return {}
            
        signals = CustomerBehaviorService.evaluate(db, customer_id)
            
        return {
            "customer_id": customer.id,
            "status": customer.status,
            "profile": {
                "transaction_count": profile.transaction_count if profile else 0,
                "transaction_volume": profile.transaction_volume if profile else 0,
                "average_transaction_amount": profile.average_transaction_amount if profile else 0,
                "active_days": profile.active_days if profile else 0,
                "lifecycle_state": profile.lifecycle_state if profile else "NEW",
                "behavioral_stability": profile.behavioral_stability if profile else "STABLE",
            },
            "segment": {
                "segment_name": segment.segment_name if segment else "NEW",
                "evidence": segment.evidence if segment else "Customer is new"
            },
            "signals": [s.model_dump() for s in signals]
        }
