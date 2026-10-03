with open("app/worker.py", "r") as f:
    content = f.read()

# Add Merchant and Agent imports
if "from app.services.merchant_intelligence import MerchantProfileService, MerchantBehaviorService, MerchantSignalAdapter" not in content:
    content = content.replace("from app.services.financial_intelligence import FinancialProfileService, FinancialBehaviorService, FinancialSignalAdapter", 
                              "from app.services.financial_intelligence import FinancialProfileService, FinancialBehaviorService, FinancialSignalAdapter\nfrom app.services.merchant_intelligence import MerchantProfileService, MerchantBehaviorService, MerchantSignalAdapter\nfrom app.services.agent_intelligence import AgentProfileService, AgentBehaviorService, AgentSignalAdapter")

# Update process_transaction_event to build Merchant and Agent Profiles
old_block_tx = """            # Build Graph, Customer and Financial Profiles
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)
                    CustomerProfileService.process_transaction(db, tx)
                    FinancialProfileService.process_transaction(db, tx)"""

new_block_tx = """            # Build Graph, Customer, Financial, Merchant and Agent Profiles
            if event_type in ["transaction.received", "transaction.completed"]:
                tx = db.query(Transaction).filter_by(id=tx_id).first()
                if tx:
                    GraphBuilder.process_transaction(db, tx)
                    CustomerProfileService.process_transaction(db, tx)
                    FinancialProfileService.process_transaction(db, tx)
                    MerchantProfileService.process_transaction(db, tx)
                    AgentProfileService.process_transaction(db, tx)"""

if "MerchantProfileService.process_transaction" not in content:
    content = content.replace(old_block_tx, new_block_tx)

# Update process_risk_evaluation to include Merchant and Agent Signals
old_block_risk = """                financial_signals = FinancialBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(FinancialSignalAdapter.adapt(financial_signals))
        
        engine = UnifiedRiskEngine(db)"""

new_block_risk = """                financial_signals = FinancialBehaviorService.evaluate(db, sender_account.customer_id)
                signals.extend(FinancialSignalAdapter.adapt(financial_signals))
            
            # Merchant Signals (If applicable)
            if tx.merchant_id:
                merchant_signals = MerchantBehaviorService.evaluate(db, tx.merchant_id)
                signals.extend(MerchantSignalAdapter.adapt(merchant_signals))
                
            # Agent Signals (If applicable)
            if tx.agent_id:
                agent_signals = AgentBehaviorService.evaluate(db, tx.agent_id)
                signals.extend(AgentSignalAdapter.adapt(agent_signals))
        
        engine = UnifiedRiskEngine(db)"""

if "MerchantBehaviorService.evaluate" not in content:
    content = content.replace(old_block_risk, new_block_risk)

with open("app/worker.py", "w") as f:
    f.write(content)
