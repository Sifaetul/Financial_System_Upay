import sys
import os
import uuid
import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.database import SessionLocal
from app.models.transaction import Transaction
from app.services.risk_engine import UnifiedRiskEngine
from app.schemas.risk import RiskContext
from app.services.competition_service import CompetitionService

def test_e2e():
    db = SessionLocal()
    
    # Run Risk Evolution on existing tx
    tx = db.query(Transaction).first()
    if not tx:
        print("NO TRANSACTION FOUND!")
        return

    print("--- REAL E2E EVIDENCE ---")
    print(f"Transaction ID: {tx.id}")
    
    # Fraud Ring Logic (Network Analysis)
    network_signal = CompetitionService.detect_fraud_ring(db, tx.sender_account_id)
    print(f"Network Threat ID: {network_signal.id if network_signal else 'NONE'}")
    
    # What-If Simulation
    context = RiskContext(transaction_id=tx.id, event_id="evt", correlation_id="corr", causation_id="cause", amount=tx.amount, currency=tx.currency, channel="WEB", transaction_type="TRANSFER", timestamp=datetime.datetime.now(datetime.UTC))
    sim = CompetitionService.simulate_what_if(db, context, [])
    print(f"Simulation ID: {sim.id}, Baseline Comparison: {sim.baseline_comparison}")
    
    # Replay
    # Let's just create an evaluation natively and then replay it
    context = RiskContext(transaction_id=tx.id, event_id="evt2", correlation_id="corr2", causation_id="cause2", amount=tx.amount, currency=tx.currency, channel="API", transaction_type="TRANSFER", timestamp=datetime.datetime.now(datetime.UTC))
    engine = UnifiedRiskEngine(db)
    evaluation = engine.evaluate(context, [])
    print(f"Risk Evaluation ID: {evaluation.id}")
    
    replay = CompetitionService.replay_decision(db, evaluation.id)
    print(f"Replay ID: {replay.id}, Divergence: {replay.divergence}")
    
    print("SUCCESS")
    
if __name__ == "__main__":
    test_e2e()
