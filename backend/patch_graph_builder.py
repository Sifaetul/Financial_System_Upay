with open("app/services/graph_intelligence.py", "r") as f:
    content = f.read()

old_builder = """class GraphBuilder:
    @staticmethod
    def process_transaction(db: Session, transaction: Transaction):
        repo = GraphRepository(db)
        
        # Accounts
        sender_node = repo.get_or_create_node("ACCOUNT", transaction.sender_account_id)
        if transaction.receiver_account_id:
            receiver_node = repo.get_or_create_node("ACCOUNT", transaction.receiver_account_id)
            repo.upsert_edge(sender_node, receiver_node, "TRANSFERS_TO", transaction.amount)
            
        # Device
        if transaction.device_id:
            device_node = repo.get_or_create_node("DEVICE", transaction.device_id)
            repo.upsert_edge(sender_node, device_node, "USES_DEVICE")
"""

new_builder = """class GraphBuilder:
    @staticmethod
    def process_transaction(db: Session, transaction: Transaction):
        repo = GraphRepository(db)
        
        # Accounts
        sender_node = repo.get_or_create_node("ACCOUNT", transaction.sender_account_id)
        
        # Link to customer (Sender)
        sender_account = db.query(Account).filter_by(id=transaction.sender_account_id).first()
        customer_node = None
        if sender_account:
            customer_node = repo.get_or_create_node("CUSTOMER", sender_account.customer_id)
            repo.upsert_edge(customer_node, sender_node, "OWNS_ACCOUNT")
            
        if transaction.receiver_account_id:
            receiver_node = repo.get_or_create_node("ACCOUNT", transaction.receiver_account_id)
            repo.upsert_edge(sender_node, receiver_node, "TRANSFERS_TO", transaction.amount)
            
        # Device
        if transaction.device_id:
            device_node = repo.get_or_create_node("DEVICE", transaction.device_id)
            repo.upsert_edge(sender_node, device_node, "USES_DEVICE")
            
        # Merchant (Phase 10)
        if transaction.merchant_id and customer_node:
            merchant_node = repo.get_or_create_node("MERCHANT", transaction.merchant_id)
            repo.upsert_edge(customer_node, merchant_node, "TRANSACTS_WITH", transaction.amount)
            
        # Agent (Phase 10)
        if transaction.agent_id and customer_node:
            agent_node = repo.get_or_create_node("AGENT", transaction.agent_id)
            repo.upsert_edge(customer_node, agent_node, "USES_AGENT", transaction.amount)
"""

if "merchant_node = repo.get_or_create_node(\"MERCHANT\"" not in content:
    content = content.replace(old_builder, new_builder)

with open("app/services/graph_intelligence.py", "w") as f:
    f.write(content)
