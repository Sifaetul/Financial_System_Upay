import re

with open("app/core/security.py", "r") as f:
    content = f.read()

# Replace get_password_hash
old_hash = """def get_password_hash(password: str) -> str:
    # bcrypt truncates to 72 bytes, so hash with SHA256 first if we want long passwords, 
    # or just let it enforce the limit (since schema max_length is 128). We'll just encode.
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')"""

new_hash = """def get_password_hash(password: str) -> str:
    # Hash with SHA-256 first to avoid bcrypt 72-byte limit
    import hashlib
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(sha256_hash, salt).decode('utf-8')"""

content = content.replace(old_hash, new_hash)

# Replace verify_password
old_verify = """def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False"""

new_verify = """def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        import hashlib
        sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest().encode('utf-8')
        return bcrypt.checkpw(sha256_hash, hashed_password.encode('utf-8'))
    except ValueError:
        return False"""

content = content.replace(old_verify, new_verify)

with open("app/core/security.py", "w") as f:
    f.write(content)
