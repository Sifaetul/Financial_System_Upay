from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import decode_token
from app.models.identity import User
import time
import redis
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

try:
    redis_client = redis.from_url(settings.REDIS_URI, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = None

# Fallback in-memory store for tests when Redis is down
_test_rate_limit_store = {}

def rate_limit(requests: int = 5, window: int = 60):
    def dependency(request: Request):
        import os
        if os.environ.get("TESTING"): return True
        ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{request.url.path}:{ip}"
        
        if redis_client:
            current = redis_client.get(key)
            if current and int(current) >= requests:
                raise HTTPException(status_code=429, detail="Too many requests")
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            pipe.execute()
        else:
            now = time.time()
            if key in _test_rate_limit_store:
                count, expiry = _test_rate_limit_store[key]
                if now > expiry:
                    _test_rate_limit_store[key] = (1, now + window)
                else:
                    if count >= requests:
                        raise HTTPException(status_code=429, detail="Too many requests")
                    _test_rate_limit_store[key] = (count + 1, expiry)
            else:
                _test_rate_limit_store[key] = (1, now + window)
        return True
    return dependency

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user

def require_permissions(required_permissions: List[str]):
    def dependency(current_user: User = Depends(get_current_user)):
        user_perms = set()
        for role in current_user.roles:
            for p in role.permissions.get("keys", []):
                user_perms.add(p)
                
        for req in required_permissions:
            if req not in user_perms and '*' not in user_perms:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user
    return dependency

def require_roles(required_roles: List[str]):
    def dependency(current_user: User = Depends(get_current_user)):
        user_roles = [r.name for r in current_user.roles]
        if not any(req in user_roles for req in required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough roles")
        return current_user
    return dependency

