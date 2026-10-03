with open("app/worker.py", "r") as f:
    content = f.read()

# Add GraphBuilder
if "from app.services.graph_intelligence import GraphBuilder, GraphSignalService, GraphRiskAdapter" not in content:
    content = content.replace("from app.services.fraud_intelligence import FraudIntelligenceOrchestrator", 
                              "from app.services.fraud_intelligence import FraudIntelligenceOrchestrator\nfrom app.services.graph_intelligence import GraphBuilder, GraphSignalService, GraphRiskAdapter\nfrom app.models.transaction import Transaction")

# Update process_transaction_event to build graph
old_block_tx = """            # Trigger Async Risk Evaluation for new transactions
            if event_type == "transaction.received":
                process_risk_evaluation.delay(event_id, tx_id, payload, correlation_id)"""

new_block_tx = """            # Build Graph
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)
            
            # Trigger Async Risk Evaluation for new transactions
            if event_type == "transaction.received":
                process_risk_evaluation.delay(event_id, tx_id, payload, correlation_id)"""

if "GraphBuilder.process_transaction" not in content:
    content = content.replace(old_block_tx, new_block_tx)


# Update process_risk_evaluation to include GraphSignals
old_block_risk = """        signals = FraudIntelligenceOrchestrator.evaluate(db, transaction_id, correlation_id)
        
        engine = UnifiedRiskEngine(db)"""

new_block_risk = """        signals = FraudIntelligenceOrchestrator.evaluate(db, transaction_id, correlation_id)
        
        # Merge Graph Signals
        tx = db.query(Transaction).filter_by(id=transaction_id).first()
        if tx:
            graph_fraud_signals = GraphSignalService.evaluate(db, tx.sender_account_id)
            signals.extend(GraphRiskAdapter.adapt(graph_fraud_signals))
        
        engine = UnifiedRiskEngine(db)"""

if "GraphSignalService.evaluate" not in content:
    content = content.replace(old_block_risk, new_block_risk)

with open("app/worker.py", "w") as f:
    f.write(content)
