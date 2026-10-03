import re
with open("app/services/risk_engine.py", "r") as f:
    content = f.read()

if "from app.models.intelligence import FeatureSnapshot" not in content:
    content = content.replace("from app.models.event import OutboxEvent", "from app.models.event import OutboxEvent\nfrom app.models.intelligence import FeatureSnapshot")

snapshot_logic = """
        # Feature Snapshot Persistence
        snapshot = FeatureSnapshot(
            entity_id=evaluation.id,
            features=context.model_dump(mode="json")
        )
        self.db.add(snapshot)
        
        # Publish Risk Evaluation Event via Outbox
"""
if "Feature Snapshot Persistence" not in content:
    content = content.replace("# Publish Risk Evaluation Event via Outbox", snapshot_logic)

with open("app/services/risk_engine.py", "w") as f:
    f.write(content)
