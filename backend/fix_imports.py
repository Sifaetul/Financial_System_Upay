with open("app/models/intelligence.py", "r") as f:
    content = f.read()

content = content.replace("from sqlalchemy import String, Float, ForeignKey, JSON", "from sqlalchemy import String, Float, ForeignKey, JSON, UniqueConstraint, Integer, DateTime")

with open("app/models/intelligence.py", "w") as f:
    f.write(content)
