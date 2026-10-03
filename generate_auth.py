import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

def append_file(path, content):
    with open(path, "a") as f:
        f.write("\n" + content.strip() + "\n")

# 1. Models update
write_file("backend/app/models/auth.py", """
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from .base import Base, TimestampMixin, generate_uuid
from datetime import datetime

class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    family_id: Mapped[str] = mapped_column(String, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
""")

append_file("backend/app/models/__init__.py", "from .auth import RefreshToken")

# 2. Config update
append_file("backend/app/core/config.py", """
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
""")

# 3. Security Core
write_file("backend/app/core/security.py", """
import jwt
from datetime import datetime, timedelta, UTC
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, roles: list[str]) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "roles": roles, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str, family_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "family_id": family_id, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
""")

# 4. Schemas
write_file("backend/app/schemas/auth.py", """
from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
""")

# 5. Dependencies
write_file("backend/app/api/deps.py", """
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

# Minimal rate limiter (Token bucket or simple sliding window using Redis)
# For Phase 3 we do a simple IP-based counter if Redis is alive
try:
    redis_client = redis.from_url(settings.REDIS_URI, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = None

def rate_limit(requests: int = 5, window: int = 60):
    def dependency(request: Request):
        if not redis_client:
            return True # Fallback if redis is down
        ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{request.url.path}:{ip}"
        
        current = redis_client.get(key)
        if current and int(current) >= requests:
            raise HTTPException(status_code=429, detail="Too many requests")
        
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        pipe.execute()
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
            if req not in user_perms:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user
    return dependency
""")

# 6. Auth Endpoints
write_file("backend/app/api/v1/endpoints/auth.py", """
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.identity import User, Role
from app.models.auth import RefreshToken
from app.models.audit import AuditLog
from app.schemas.auth import UserCreate, UserResponse, Token, RefreshRequest
from app.api.deps import get_current_user, rate_limit
import uuid
from datetime import datetime, UTC

router = APIRouter()

def log_audit(db: Session, actor_id: str, action: str, resource: str):
    log = AuditLog(actor_id=actor_id, action=action, resource=resource)
    db.add(log)
    db.commit()

@router.post("/register", response_model=UserResponse, dependencies=[Depends(rate_limit(5, 60))])
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_in.password != user_in.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Check basic password policy (e.g. not common weak)
    if user_in.password.lower() in ["password123", "qwerty", "admin"]:
        raise HTTPException(status_code=400, detail="Password is too weak")

    # Ensure USER role exists
    role = db.query(Role).filter(Role.name == "USER").first()
    if not role:
        role = Role(name="USER", permissions={"keys": ["read:own"]})
        db.add(role)
        db.commit()

    hashed = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, password_hash=hashed)
    new_user.roles.append(role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_audit(db, new_user.id, "register", "User")
    
    return UserResponse(id=new_user.id, email=new_user.email, is_active=new_user.is_active, roles=[r.name for r in new_user.roles])

@router.post("/login", response_model=Token, dependencies=[Depends(rate_limit(10, 60))])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        log_audit(db, form_data.username, "login_failed", "Auth")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    family_id = str(uuid.uuid4())
    access_token = create_access_token(subject=user.id, roles=[r.name for r in user.roles])
    refresh_jwt = create_refresh_token(subject=user.id, family_id=family_id)
    
    # Store refresh token state (hash it for security if needed, or store JTI)
    payload = decode_token(refresh_jwt)
    exp_time = datetime.fromtimestamp(payload["exp"], UTC)
    
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(refresh_jwt),
        family_id=family_id,
        expires_at=exp_time
    )
    db.add(db_token)
    db.commit()
    
    log_audit(db, user.id, "login_success", "Auth")
    
    return {"access_token": access_token, "refresh_token": refresh_jwt, "token_type": "bearer"}

@router.post("/refresh", response_model=Token, dependencies=[Depends(rate_limit(5, 60))])
def refresh_token(req: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    user_id = payload.get("sub")
    family_id = payload.get("family_id")
    
    # Find active token belonging to this family
    db_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.family_id == family_id
    ).all()
    
    matching_token = None
    for token in db_tokens:
        if verify_password(req.refresh_token, token.token_hash):
            matching_token = token
            break
            
    if not matching_token:
        # Suspicious reuse detected! Invalidate the whole family.
        for t in db_tokens:
            t.is_revoked = True
        db.commit()
        log_audit(db, user_id, "refresh_reuse_detected", "Auth")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    if matching_token.is_revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked")
        
    if matching_token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Rotate
    matching_token.is_revoked = True
    
    new_access = create_access_token(subject=user.id, roles=[r.name for r in user.roles])
    new_refresh = create_refresh_token(subject=user.id, family_id=family_id)
    
    new_payload = decode_token(new_refresh)
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(new_refresh),
        family_id=family_id,
        expires_at=datetime.fromtimestamp(new_payload["exp"], UTC)
    )
    db.add(new_db_token)
    db.commit()
    
    log_audit(db, user.id, "refresh_success", "Auth")
    
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

@router.post("/logout")
def logout(req: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if payload:
        family_id = payload.get("family_id")
        user_id = payload.get("sub")
        
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.family_id == family_id
        ).all()
        
        for t in tokens:
            t.is_revoked = True
        db.commit()
        log_audit(db, user_id, "logout", "Auth")
        
    return {"status": "logged out"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id, 
        email=current_user.email, 
        is_active=current_user.is_active, 
        roles=[r.name for r in current_user.roles]
    )
""")

# 7. Update router
write_file("backend/app/api/v1/router.py", """
from fastapi import APIRouter
from .endpoints import health
from .endpoints import auth

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
""")

# 8. Add Security Headers to main.py
write_file("backend/app/main.py", """
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import custom_exception_handler

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

app.add_exception_handler(Exception, custom_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)
""")

# 9. Tests
write_file("backend/tests/test_auth.py", """
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.core.config import settings
from app.models.base import Base

engine = create_engine(settings.DATABASE_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_register_and_login():
    # Register
    reg_response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    assert reg_response.status_code == 200
    data = reg_response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data

    # Login
    login_response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "StrongPassword123!"
    })
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test@example.com"

def test_login_invalid_password():
    client.post("/api/v1/auth/register", json={
        "email": "bad@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    res = client.post("/api/v1/auth/login", data={"username": "bad@example.com", "password": "wrong"})
    assert res.status_code == 401

def test_refresh_token_rotation():
    client.post("/api/v1/auth/register", json={
        "email": "rot@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    login_res = client.post("/api/v1/auth/login", data={"username": "rot@example.com", "password": "StrongPassword123!"})
    tokens = login_res.json()
    old_refresh = tokens["refresh_token"]

    # Refresh
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert ref_res.status_code == 200
    new_refresh = ref_res.json()["refresh_token"]

    # Try old refresh again (Reuse detection!)
    ref_res_bad = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert ref_res_bad.status_code == 401

    # Try new refresh (Should fail because family was revoked!)
    ref_res_bad2 = client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert ref_res_bad2.status_code == 401

def test_logout():
    client.post("/api/v1/auth/register", json={
        "email": "logout@example.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!"
    })
    login_res = client.post("/api/v1/auth/login", data={"username": "logout@example.com", "password": "StrongPassword123!"})
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    res = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert res.status_code == 200

    # Try refresh
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == 401
""")

