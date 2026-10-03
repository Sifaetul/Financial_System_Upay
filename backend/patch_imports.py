with open("app/models/transaction.py", "r") as f:
    content = f.read()

import_str = "from sqlalchemy.orm import Mapped, mapped_column, relationship\nfrom sqlalchemy import String, ForeignKey, Float, Integer, DateTime, JSON\nfrom datetime import datetime, UTC"

if "Integer" not in content[:500]:
    content = import_str + "\n" + content.replace("from sqlalchemy.orm import Mapped, mapped_column, relationship\nfrom sqlalchemy import String, ForeignKey, Float", "")

with open("app/models/transaction.py", "w") as f:
    f.write(content)
