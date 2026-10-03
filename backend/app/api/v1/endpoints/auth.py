from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token, get_token_hash
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
        token_hash=get_token_hash(refresh_jwt),
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
        if get_token_hash(req.refresh_token) == token.token_hash:
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
        for t in db_tokens:
            t.is_revoked = True
        db.commit()
        log_audit(db, user_id, "refresh_reuse_detected", "Auth")
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
        token_hash=get_token_hash(new_refresh),
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
