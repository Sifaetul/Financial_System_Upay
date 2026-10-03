with open("app/services/fraud_intelligence.py", "r") as f:
    content = f.read()

content = content.replace("from typing import List, Dict", "from typing import List, Dict, Any")

with open("app/services/fraud_intelligence.py", "w") as f:
    f.write(content)
