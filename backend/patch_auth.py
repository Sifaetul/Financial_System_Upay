import re

with open("app/api/v1/endpoints/auth.py", "r") as f:
    content = f.read()

replacement = """
    if matching_token.is_revoked:
        for t in db_tokens:
            t.is_revoked = True
        db.commit()
        log_audit(db, user_id, "refresh_reuse_detected", "Auth")
        raise HTTPException(status_code=401, detail="Refresh token revoked")
"""

content = re.sub(r'    if matching_token\.is_revoked:\n        raise HTTPException\(status_code=401, detail="Refresh token revoked"\)', replacement, content)

with open("app/api/v1/endpoints/auth.py", "w") as f:
    f.write(content)
