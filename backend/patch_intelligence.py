import re
with open("app/models/intelligence.py", "r") as f:
    content = f.read()

# Remove Alert, Case, CaseEvent classes
content = re.sub(r'class Alert\(Base, TimestampMixin\):.*?(?=class RiskScore)', '', content, flags=re.DOTALL)

with open("app/models/intelligence.py", "w") as f:
    f.write(content)

with open("app/models/__init__.py", "r") as f:
    init_content = f.read()

# Update import in __init__.py
init_content = init_content.replace("RuleVersion, Alert, Case, CaseEvent, RiskScore", "RuleVersion, RiskScore")
with open("app/models/__init__.py", "w") as f:
    f.write(init_content)
