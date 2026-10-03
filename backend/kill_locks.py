from sqlalchemy import create_engine, text
engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/upay_nexus", isolation_level="AUTOCOMMIT")
with engine.connect() as conn:
    conn.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'upay_nexus' AND pid <> pg_backend_pid();"))
    print("Killed all other connections.")
