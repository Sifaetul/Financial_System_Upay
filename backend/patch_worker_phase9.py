with open("app/worker.py", "r") as f:
    content = f.read()

# Add Financial imports
if "from app.services.financial_intelligence import FinancialProfileService, FinancialBehaviorService, FinancialSignalAdapter" not in content:
    content = content.replace("from app.services.customer_intelligence import CustomerProfileService, CustomerBehaviorService, CustomerSignalAdapter", 
                              "from app.services.customer_intelligence import CustomerProfileService, CustomerBehaviorService, CustomerSignalAdapter\nfrom app.services.financial_intelligence import FinancialProfileService, FinancialBehaviorService, FinancialSignalAdapter")

# Update process_transaction_event to build Financial Profile
old_block_tx = """            # Build Graph and Customer Profile
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)
                    CustomerProfileService.process_transaction(db, tx)"""

new_block_tx = """            # Build Graph, Customer and Financial Profiles
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)
                    CustomerProfileService.process_transaction(db, tx)
                    FinancialProfileService.process_transaction(db, tx)"""

if "FinancialProfileService.process_transaction" not in content:
    content = content.replace(old_block_tx, new_block_tx)

# Update process_risk_evaluation to include Financial Signals
old_block_risk = """            sender_account = db.query(Account).filter_by(id=tx.sender_account_id).first()
            if sender_account:
                customer_signals = CustomerBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(CustomerSignalAdapter.adapt(customer_signals))
        
        engine = UnifiedRiskEngine(db)"""

new_block_risk = """            sender_account = db.query(Account).filter_by(id=tx.sender_account_id).first()
            if sender_account:
                customer_signals = CustomerBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(CustomerSignalAdapter.adapt(customer_signals))
                
                financial_signals = FinancialBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(FinancialSignalAdapter.adapt(financial_signals))
        
        engine = UnifiedRiskEngine(db)"""

if "FinancialBehaviorService.evaluate" not in content:
    content = content.replace(old_block_risk, new_block_risk)

with open("app/worker.py", "w") as f:
    f.write(content)
