import glob

migrations = glob.glob("alembic/versions/*_phase_11_real_investigation_models.py")
migration_file = migrations[0]

with open(migration_file, "r") as f:
    content = f.read()

# Make sure drop_table('case_events') comes before drop_table('cases')
content = content.replace("op.drop_table('cases')\n    op.drop_table('case_events')", "op.drop_table('case_events')\n    op.drop_table('cases')")
content = content.replace("op.drop_index('ix_case_events_case_id', table_name='case_events')\n    ", "")
content = content.replace("op.drop_index('ix_cases_status', table_name='cases')\n    ", "")
content = content.replace("op.drop_index('ix_cases_alert_id', table_name='cases')\n    ", "")


with open(migration_file, "w") as f:
    f.write(content)
