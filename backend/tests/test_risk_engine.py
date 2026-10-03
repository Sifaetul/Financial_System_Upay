import pytest
from app.services.risk_engine import UnifiedRiskEngine, RiskDecisionPolicy
from app.schemas.risk import RiskContext, RiskSignalInput
from datetime import datetime, UTC

def test_risk_decision_policy():
    policy = RiskDecisionPolicy("1.0")
    assert policy.map_score_to_category(0.9) == "CRITICAL"
    assert policy.map_score_to_category(0.7) == "HIGH"
    assert policy.map_score_to_category(0.4) == "MEDIUM"
    assert policy.map_score_to_category(0.2) == "LOW"
    assert policy.map_score_to_category(0.1) == "VERY_LOW"
    
    assert policy.map_category_to_decision("CRITICAL") == "BLOCK"
    assert policy.map_category_to_decision("HIGH") == "STEP_UP"

def test_risk_fusion_logic():
    from app.core.database import SessionLocal
    db_session = SessionLocal()
    engine = UnifiedRiskEngine(db_session)

    from app.models.customer import Customer, Account
    from app.models.transaction import Transaction
    import uuid
    
    cust = Customer(identifier=str(uuid.uuid4()))
    db_session.add(cust)
    db_session.commit()
    db_session.refresh(cust)
    
    acc = Account(customer_id=cust.id, account_number_hash=str(uuid.uuid4()))
    db_session.add(acc)
    db_session.commit()
    db_session.refresh(acc)
    
    tx = Transaction(amount=100.0, currency="USD", transaction_type="SEND_MONEY", sender_account_id=acc.id, receiver_account_id=acc.id, status="RECEIVED", idempotency_key=str(uuid.uuid4()))
    db_session.add(tx)
    db_session.commit()
    db_session.refresh(tx)
    
    context = RiskContext(
        transaction_id=tx.id, amount=100.0, currency="USD",
        transaction_type="SEND_MONEY", timestamp=datetime.now(UTC),
        correlation_id="corr_1"
    )

    
    signals = [
        RiskSignalInput(
            signal_id="sig1", signal_type="velocity", source="rule1",
            raw_value="high", normalized_value=1.0, weight=1.0,
            confidence=1.0, reliability=1.0, explanation="High velocity", provenance={}
        ),
        RiskSignalInput(
            signal_id="sig2", signal_type="amount", source="rule2",
            raw_value=100, normalized_value=0.0, weight=1.0,
            confidence=1.0, reliability=1.0, explanation="Low amount", provenance={}
        )
    ]
    
    # Fusion calculation:
    # sig1: weight=1, norm=1.0 -> contrib = 1.0
    # sig2: weight=1, norm=0.0 -> contrib = 0.0
    # total weight = 2.0
    # expected score = 1.0 / 2.0 = 0.5 (MEDIUM)
    
    ev = engine.evaluate(context, signals)
    assert ev.score == 0.5
    assert ev.category == "MEDIUM"
    assert ev.decision == "REVIEW"
    assert ev.confidence_summary == 1.0
    assert len(ev.signals) == 2
    assert "velocity" in ev.explanation
    db_session.close()
