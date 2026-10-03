import re
with open("app/services/risk_engine.py", "r") as f:
    c = f.read()

c = c.replace("MonitoringService.log_metric(db,", "MonitoringService.log_metric(self.db,")

with open("app/services/risk_engine.py", "w") as f:
    f.write(c)
