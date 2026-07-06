from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas.auth import Token, LoginCredentials, RefreshRequest, UserRegistrationRequest
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user
from app.core.jwt import decode_token, create_access_token, create_refresh_token
from app.core.permissions import get_current_user
from app.core.security import hash_password
from app.models.user import User
import uuid
import secrets

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(credentials: LoginCredentials, db: AsyncSession = Depends(get_db)):
    """Authenticate and get tokens."""
    return await authenticate_user(db, credentials)

@router.post("/register")
async def register(request: UserRegistrationRequest, db: AsyncSession = Depends(get_db)):
    """Self-register a new employee."""
    
    # Check if email exists
    result = await db.execute(select(User).filter(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Generate unique employee ID: EMP-XXXX
    emp_hash = secrets.token_hex(2).upper()
    employee_id = f"EMP-{emp_hash}"
    
    new_user = User(
        employee_id=employee_id,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        department=request.department,
        password_hash=hash_password(request.password),
        role="employee",
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "message": "Registration successful",
        "employee_id": employee_id,
        "first_name": request.first_name
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token."""
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
            
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid subject")
            
        # Get user to ensure they still exist and are active
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise ValueError("User inactive or deleted")
            
        access_token = create_access_token(
            subject=user.id, email=user.email, role=user.role
        )
        refresh_token = create_refresh_token(subject=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint. For JWT, mostly handled client-side by dropping tokens."""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info (deprecated, use /api/users/me)."""
    return current_user
