from app.core.database import engine
from app.models.base import Base
import app.models
from sqlalchemy import text

print("Creating tables...")
Base.metadata.create_all(engine)

with engine.connect() as conn:
    res = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public';")).fetchall()
    print("Tables in public schema:", [r[0] for r in res])
