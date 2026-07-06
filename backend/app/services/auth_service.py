from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.user import User
from app.schemas.auth import LoginCredentials
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token

async def authenticate_user(db: AsyncSession, credentials: LoginCredentials):
    """Authenticate a user and return tokens."""
    # Find user by employee_id
    result = await db.execute(select(User).filter(User.employee_id == credentials.employee_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect employee ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect employee ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.add(user)
    await db.commit()

    # Generate tokens
    access_token = create_access_token(
        subject=user.id, email=user.email, role=user.role
    )
    refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
