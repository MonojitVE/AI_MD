from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import EmailStr

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.permissions import get_current_user, require_admin
from app.core.security import hash_password

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user. Admin only."""
    # Check if employee_id exists
    result = await db.execute(select(User).filter(User.employee_id == user_in.employee_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Employee ID already registered")
        
    # Check if email exists
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user_in.model_dump(exclude={"password"})
    user_data["password_hash"] = hash_password(user_in.password)
    
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all users. Admin only."""
    result = await db.execute(select(User))
    return result.scalars().all()

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile."""
    # Employees can't change their role or employee_id
    if user_update.role is not None and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to change role")
        
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
        
    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user by ID. Admin only."""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
        
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user. Admin only."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.delete(user)
    await db.commit()
