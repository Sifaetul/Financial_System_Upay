from sqlalchemy import create_engine, text
engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/upay_nexus")
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()
