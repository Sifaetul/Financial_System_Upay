import re

with open("app/worker.py", "r") as f:
    content = f.read()

# Remove the broken block from process_risk_evaluation
broken_block = """        # Trigger Async Risk Evaluation after commit to avoid deadlock in eager mode
        if event_type == "transaction.received":
            process_risk_evaluation.delay(event_id, tx_id, payload, correlation_id)"""

# We want to replace only the LAST occurrence (which is inside process_risk_evaluation)
last_idx = content.rfind(broken_block)
if last_idx != -1:
    content = content[:last_idx] + content[last_idx + len(broken_block):]

with open("app/worker.py", "w") as f:
    f.write(content)
