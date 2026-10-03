from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Tuple
import math

from app.models.customer import Customer, Account, FinancialProfile
from app.models.transaction import Transaction
from app.schemas.fraud import FraudSignal
from app.schemas.risk import RiskSignalInput

class FinancialProfileService:
    @staticmethod
    def process_transaction(db: Session, transaction: Transaction):
        # Determine involved customer(s)
        involved_customer_ids = set()
        
        sender = db.query(Account).filter_by(id=transaction.sender_account_id).first()
        if sender:
            involved_customer_ids.add(sender.customer_id)
            
        receiver = None
        if transaction.receiver_account_id:
            receiver = db.query(Account).filter_by(id=transaction.receiver_account_id).first()
            if receiver:
                involved_customer_ids.add(receiver.customer_id)
                
        for customer_id in involved_customer_ids:
            FinancialProfileService._update_profile(db, customer_id)
            
    @staticmethod
    def _update_profile(db: Session, customer_id: str):
        profile = db.query(FinancialProfile).filter_by(customer_id=customer_id).first()
        if not profile:
            profile = FinancialProfile(customer_id=customer_id)
            db.add(profile)
            db.flush()
            
        now = datetime.now(UTC)
        profile.last_calculated_at = now
        
        # Get all customer accounts
        customer_accounts = {acc.id for acc in db.query(Account).filter_by(customer_id=customer_id).all()}
        
        # Get all transactions involving these accounts
        # This includes sender OR receiver
        txs = db.query(Transaction).filter(
            (Transaction.sender_account_id.in_(customer_accounts)) | 
            (Transaction.receiver_account_id.in_(customer_accounts))
        ).all()
        
        inflows = 0.0
        outflows = 0.0
        inflow_count = 0
        outflow_count = 0
        
        min_date = now
        
        for tx in txs:
            if tx.created_at and tx.created_at < min_date:
                min_date = tx.created_at
                
            is_sender = tx.sender_account_id in customer_accounts
            is_receiver = tx.receiver_account_id in customer_accounts
            
            # Internal Transfer (both accounts owned by customer)
            if is_sender and is_receiver:
                continue # Do not double count
                
            if is_sender:
                outflows += tx.amount
                outflow_count += 1
            elif is_receiver:
                inflows += tx.amount
                inflow_count += 1
                
        profile.observation_start = min_date
        profile.observation_end = now
        profile.total_inflow = inflows
        profile.total_outflow = outflows
        profile.net_cash_flow = inflows - outflows
        profile.inflow_transaction_count = inflow_count
        profile.outflow_transaction_count = outflow_count
        
        days = (now - min_date).days
        if days < 1:
            days = 1
            
        profile.average_daily_inflow = inflows / days
        profile.average_daily_outflow = outflows / days
        
        if days >= 7:
            profile.data_sufficiency = "SUFFICIENT_DATA"
            
            # Simple Health Logic
            if profile.net_cash_flow > 0 and inflows > 0:
                profile.financial_health_score = "STABLE"
            elif profile.net_cash_flow < 0:
                profile.financial_health_score = "PRESSURED"
            else:
                profile.financial_health_score = "WATCH"
        else:
            profile.data_sufficiency = "INSUFFICIENT_DATA"
            profile.financial_health_score = "UNAVAILABLE"
            
        # Update Forecasting
        if profile.data_sufficiency == "SUFFICIENT_DATA":
            CashFlowForecastingService.evaluate(profile, txs, customer_accounts, days)

        profile.profile_version += 1
        db.flush()

class CashFlowForecastingService:
    @staticmethod
    def evaluate(profile: FinancialProfile, txs: List[Transaction], customer_accounts: set, days_active: int):
        # Simplified Daily Cash Flow moving average forecast
        daily_net = {}
        for tx in txs:
            if not tx.created_at: continue
            day = tx.created_at.date().isoformat()
            
            is_sender = tx.sender_account_id in customer_accounts
            is_receiver = tx.receiver_account_id in customer_accounts
            if is_sender and is_receiver: continue
            
            val = 0.0
            if is_receiver: val += tx.amount
            if is_sender: val -= tx.amount
                
            daily_net[day] = daily_net.get(day, 0.0) + val
            
        if len(daily_net) < 3:
            profile.forecast_data = {"status": "INSUFFICIENT_DATA"}
            return
            
        # Very simple validation: use first half to predict second half avg
        days_sorted = sorted(daily_net.keys())
        mid = len(days_sorted) // 2
        train_vals = [daily_net[d] for d in days_sorted[:mid]]
        test_vals = [daily_net[d] for d in days_sorted[mid:]]
        
        train_avg = sum(train_vals) / len(train_vals) if train_vals else 0
        actual_test_avg = sum(test_vals) / len(test_vals) if test_vals else 0
        mae = abs(train_avg - actual_test_avg)
        
        # 30 day forecast is train_avg * 30
        profile.forecast_data = {
            "status": "SUFFICIENT_DATA",
            "forecast_period": "30_days",
            "predicted_net_cash_flow": train_avg * 30,
            "method": "historical_daily_average",
            "validation_mae": mae,
            "confidence": 0.7 if mae < abs(train_avg) * 0.5 else 0.4
        }

class FinancialBehaviorService:
    @staticmethod
    def evaluate(db: Session, customer_id: str) -> List[FraudSignal]:
        signals = []
        profile = db.query(FinancialProfile).filter_by(customer_id=customer_id).first()
        
        if not profile or profile.data_sufficiency == "INSUFFICIENT_DATA":
            return signals
            
        if profile.financial_health_score == "PRESSURED":
            signals.append(FraudSignal(
                signal_type="NEGATIVE_NET_CASH_FLOW",
                provider="FinancialIntelligence",
                raw_value=profile.net_cash_flow,
                normalized_value=min(abs(profile.net_cash_flow) / 10000.0, 1.0),
                weight=0.7,
                confidence=0.85,
                reliability=0.9,
                severity="HIGH",
                evidence=f"Overall net cash flow is negative: {profile.net_cash_flow:.2f}",
                explanation="Customer cash outflow is significantly exceeding inflow.",
                provenance={"detector_version": "1.0", "source": "CashFlowAnalyzer"}
            ))
            
        if profile.forecast_data and profile.forecast_data.get("predicted_net_cash_flow", 0) < 0:
            signals.append(FraudSignal(
                signal_type="FINANCIAL_STRESS_INDICATOR",
                provider="FinancialIntelligence",
                raw_value=profile.forecast_data.get("predicted_net_cash_flow", 0),
                normalized_value=0.8,
                weight=0.6,
                confidence=profile.forecast_data.get("confidence", 0.5),
                reliability=0.8,
                severity="MEDIUM",
                evidence=f"Forecasted 30-day cash flow is negative: {profile.forecast_data.get('predicted_net_cash_flow'):.2f}",
                explanation="Financial stability trend is deteriorating.",
                provenance={"detector_version": "1.0", "source": "CashFlowForecaster"}
            ))
            
        return signals

class FinancialSignalAdapter:
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
