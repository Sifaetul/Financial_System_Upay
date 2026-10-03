with open("app/worker.py", "r") as f:
    content = f.read()

# Add Customer imports
if "from app.services.customer_intelligence import CustomerProfileService, CustomerBehaviorService, CustomerSignalAdapter" not in content:
    content = content.replace("from app.services.graph_intelligence import GraphBuilder, GraphSignalService, GraphRiskAdapter", 
                              "from app.services.graph_intelligence import GraphBuilder, GraphSignalService, GraphRiskAdapter\nfrom app.services.customer_intelligence import CustomerProfileService, CustomerBehaviorService, CustomerSignalAdapter")

# Update process_transaction_event to build Customer Profile
old_block_tx = """            # Build Graph
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)"""

new_block_tx = """            # Build Graph and Customer Profile
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)
                    CustomerProfileService.process_transaction(db, tx)"""

if "CustomerProfileService.process_transaction" not in content:
    content = content.replace(old_block_tx, new_block_tx)


# Update process_risk_evaluation to include Customer Signals
old_block_risk = """        # Merge Graph Signals
        tx = db.query(Transaction).filter_by(id=transaction_id).first()
        if tx:
            graph_fraud_signals = GraphSignalService.evaluate(db, tx.sender_account_id)
            signals.extend(GraphRiskAdapter.adapt(graph_fraud_signals))
        
        engine = UnifiedRiskEngine(db)"""

new_block_risk = """        # Merge Graph and Customer Signals
        tx = db.query(Transaction).filter_by(id=transaction_id).first()
        if tx:
            graph_fraud_signals = GraphSignalService.evaluate(db, tx.sender_account_id)
            signals.extend(GraphRiskAdapter.adapt(graph_fraud_signals))
            
            sender_account = db.query(Account).filter_by(id=tx.sender_account_id).first()
            if sender_account:
                customer_signals = CustomerBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(CustomerSignalAdapter.adapt(customer_signals))
        
        engine = UnifiedRiskEngine(db)"""

if "CustomerBehaviorService.evaluate" not in content:
    content = content.replace(old_block_risk, new_block_risk)

with open("app/worker.py", "w") as f:
    f.write(content)
