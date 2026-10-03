with open("app/services/customer_intelligence.py", "r") as f:
    content = f.read()

old_logic = """        txs_30d = [t for t in txs if t.created_at and t.created_at >= now - timedelta(days=30)]
        txs_7d = [t for t in txs_30d if t.created_at >= now - timedelta(days=7)]
        
        if len(txs_30d) < 3:
            return signals # INSUFFICIENT_HISTORY
            
        avg_30d = sum(t.amount for t in txs_30d) / len(txs_30d) if txs_30d else 0
        avg_7d = sum(t.amount for t in txs_7d) / len(txs_7d) if txs_7d else 0
        
        if avg_30d > 0 and avg_7d > avg_30d * 3.0:"""

new_logic = """        txs_30d = [t for t in txs if t.created_at and t.created_at >= now - timedelta(days=30)]
        txs_7d = [t for t in txs_30d if t.created_at >= now - timedelta(days=7)]
        txs_historical = [t for t in txs_30d if t.created_at < now - timedelta(days=7)]
        
        if len(txs_historical) < 3:
            return signals # INSUFFICIENT_HISTORY
            
        avg_hist = sum(t.amount for t in txs_historical) / len(txs_historical) if txs_historical else 0
        avg_7d = sum(t.amount for t in txs_7d) / len(txs_7d) if txs_7d else 0
        
        if avg_hist > 0 and avg_7d > avg_hist * 3.0:"""

content = content.replace(old_logic, new_logic)
content = content.replace("avg_30d * 5.0", "avg_hist * 5.0")
content = content.replace("{avg_30d:.2f}", "{avg_hist:.2f}")

with open("app/services/customer_intelligence.py", "w") as f:
    f.write(content)
