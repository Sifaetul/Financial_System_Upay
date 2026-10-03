from sqlalchemy import create_engine, text
engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/upay_nexus", isolation_level="AUTOCOMMIT")
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT pid, state, wait_event_type, wait_event, query 
        FROM pg_stat_activity 
        WHERE datname = 'upay_nexus' AND state != 'idle';
    """))
    for row in result:
        print(row)
