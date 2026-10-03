from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any

from app.models.transaction import Transaction, Merchant, MerchantProfile
from app.models.customer import Account, Customer
from app.schemas.fraud import FraudSignal
from app.schemas.risk import RiskSignalInput

class MerchantProfileService:
    @staticmethod
    def process_transaction(db: Session, transaction: Transaction):
        if not transaction.merchant_id:
            return
            
        merchant_id = transaction.merchant_id
        profile = db.query(MerchantProfile).filter_by(merchant_id=merchant_id).first()
        
        if not profile:
            profile = MerchantProfile(merchant_id=merchant_id)
            db.add(profile)
            db.flush()
            
        txs = db.query(Transaction).filter_by(merchant_id=merchant_id).all()
        now = datetime.now(UTC)
        
        if not txs:
            return
            
        volume = sum(t.amount for t in txs)
        count = len(txs)
        
        # Customers
        # Join accounts to get unique customers
        account_ids = {t.sender_account_id for t in txs if t.sender_account_id} | {t.receiver_account_id for t in txs if t.receiver_account_id}
        accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()
        customer_ids = {a.customer_id for a in accounts}
        
        success_count = sum(1 for t in txs if t.status == "COMPLETED")
        failed_count = sum(1 for t in txs if t.status == "FAILED")
        refund_count = sum(1 for t in txs if t.transaction_type == "REFUND")
        
        amounts = sorted([t.amount for t in txs])
        median_amount = amounts[len(amounts)//2] if amounts else 0.0
        
        min_date = min((t.created_at for t in txs if t.created_at), default=now)
        days_active = (now - min_date).days
        
        profile.observation_start = min_date
        profile.observation_end = now
        profile.transaction_count = count
        profile.transaction_volume = volume
        profile.unique_customer_count = len(customer_ids)
        profile.average_transaction_amount = volume / count if count > 0 else 0
        profile.median_transaction_amount = median_amount
        profile.largest_transaction_amount = max(amounts) if amounts else 0.0
        profile.successful_transaction_count = success_count
        profile.failed_transaction_count = failed_count
        profile.refund_count = refund_count
        
        if days_active >= 30 and count >= 10:
            profile.data_sufficiency = "SUFFICIENT_HISTORY"
        elif days_active >= 7 and count >= 3:
            profile.data_sufficiency = "LIMITED_HISTORY"
        else:
            profile.data_sufficiency = "INSUFFICIENT_HISTORY"
            
        profile.profile_version += 1
        db.flush()

class MerchantBehaviorService:
    @staticmethod
    def evaluate(db: Session, merchant_id: str) -> List[FraudSignal]:
        signals = []
        profile = db.query(MerchantProfile).filter_by(merchant_id=merchant_id).first()
        
        if not profile or profile.data_sufficiency == "INSUFFICIENT_HISTORY":
            return signals
            
        txs = db.query(Transaction).filter_by(merchant_id=merchant_id).all()
        now = datetime.now(UTC)
        
        txs_30d = [t for t in txs if t.created_at and t.created_at >= now - timedelta(days=30)]
        txs_7d = [t for t in txs_30d if t.created_at >= now - timedelta(days=7)]
        txs_historical = [t for t in txs_30d if t.created_at < now - timedelta(days=7)]
        
        if len(txs_historical) < 3:
            return signals
            
        avg_hist_vol = sum(t.amount for t in txs_historical) / len(txs_historical) if txs_historical else 0
        avg_7d_vol = sum(t.amount for t in txs_7d) / len(txs_7d) if txs_7d else 0
        
        if avg_hist_vol > 0 and avg_7d_vol > avg_hist_vol * 3.0:
            signals.append(FraudSignal(
                signal_type="MERCHANT_VOLUME_SPIKE",
                provider="MerchantIntelligence",
                raw_value=avg_7d_vol,
                normalized_value=min(avg_7d_vol / (avg_hist_vol * 5.0), 1.0),
                weight=0.8,
                confidence=0.9,
                reliability=0.9,
                severity="HIGH",
                evidence=f"Recent 7-day avg volume ({avg_7d_vol:.2f}) is >3x historical ({avg_hist_vol:.2f})",
                explanation="Significant increase in merchant transaction volume.",
                provenance={"detector_version": "1.0", "source": "MerchantBehaviorDetector"}
            ))
            
        return signals

class MerchantSignalAdapter:
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
