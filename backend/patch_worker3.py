with open("app/worker.py", "r") as f:
    content = f.read()

# Remove the delay call from its original place
old_delay = """            # Trigger Async Risk Evaluation for new transactions
            if event_type == "transaction.received":
                process_risk_evaluation.delay(event_id, tx_id, payload, correlation_id)"""

new_delay = """            # Risk evaluation moved to end"""

content = content.replace(old_delay, new_delay)

# Add it after db.commit()
old_commit = """        # Mark processed
        db.add(ProcessedEvent(event_id=event_id, consumer_name=consumer_name))
        db.commit()"""

new_commit = """        # Mark processed
        db.add(ProcessedEvent(event_id=event_id, consumer_name=consumer_name))
        db.commit()
        
        # Trigger Async Risk Evaluation after commit to avoid deadlock in eager mode
        if event_type == "transaction.received":
            process_risk_evaluation.delay(event_id, tx_id, payload, correlation_id)
"""
content = content.replace(old_commit, new_commit)

with open("app/worker.py", "w") as f:
    f.write(content)
