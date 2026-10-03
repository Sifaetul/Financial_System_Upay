with open("app/worker.py", "r") as f:
    content = f.read()

imports = """from app.services.alert_engine import AlertEngine
from app.services.investigation_service import InvestigationService
import asyncio
from app.api.v1.websockets import notifier
"""

if "from app.services.alert_engine import AlertEngine" not in content:
    content = content.replace("from app.services.unified_risk_engine import UnifiedRiskEngine", imports + "from app.services.unified_risk_engine import UnifiedRiskEngine")

old_risk_eval = """        decision = engine.evaluate(tx_id, signals)
        
        # Persist decision via Phase 4 / Phase 5 adapter if needed.
        # But for now, we just let the broker process the next steps.
        
        db.commit()"""

new_risk_eval = """        decision = engine.evaluate(tx_id, signals)
        
        # Alert Generation
        alert = AlertEngine.generate_alert(db, decision)
        if alert:
            # Auto-case creation if CRITICAL
            if alert.severity == "CRITICAL":
                InvestigationService.create_case_from_alert(db, alert)
                
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            loop.run_until_complete(notifier.broadcast_alert({
                "alert_id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "entity_id": alert.entity_id,
                "risk_score": alert.risk_score
            }))
        
        db.commit()"""

if "AlertEngine.generate_alert" not in content:
    content = content.replace(old_risk_eval, new_risk_eval)

with open("app/worker.py", "w") as f:
    f.write(content)
