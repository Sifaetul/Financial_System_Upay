from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URI)
with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE;"))
    conn.execute(text("CREATE SCHEMA public;"))
    # Recreate extension
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()
print("Database cleaned.")
