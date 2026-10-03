with open("tests/test_risk_api.py", "r") as f:
    content = f.read()

role_injection = """
    db = SessionLocal()
    from app.models.identity import User, Role
    u = db.query(User).filter_by(email=email).first()
    
    # Create or update role
    import uuid
    admin_role = db.query(Role).filter_by(name="risk_admin").first()
    if not admin_role:
        admin_role = Role(name="risk_admin", permissions={"keys": ["manage_transactions"]})
        db.add(admin_role)
    else:
        admin_role.permissions = {"keys": ["manage_transactions"]}
    
    if u:
        u.roles.append(admin_role)
        db.commit()
    db.close()
"""

import re
content = re.sub(r"    db = SessionLocal\(\).*?db\.close\(\)", role_injection, content, flags=re.DOTALL)

with open("tests/test_risk_api.py", "w") as f:
    f.write(content)
