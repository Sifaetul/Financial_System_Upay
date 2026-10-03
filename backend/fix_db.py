from sqlalchemy import create_engine, text
engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/upay_nexus", isolation_level="AUTOCOMMIT")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS cases CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS alerts CASCADE;"))
    print("Dropped old alerts and cases tables.")
