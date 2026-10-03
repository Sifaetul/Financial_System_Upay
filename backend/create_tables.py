from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
import app.models

print("Creating tables...")
Base.metadata.create_all(engine)
print("Done!")
