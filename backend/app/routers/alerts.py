"""Alert management API router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from typing import Optional

from app.database import get_db
from app.models.alert import Alert
from app.models.equipment import Equipment
from app.core.permissions import require_admin, get_current_user
from pydantic import BaseModel
from datetime import datetime
from app.models.alert import MaintenanceLog
from app.models.user import User

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("")
async def list_alerts(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    is_read: Optional[bool] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all alerts with filters."""
    query = select(Alert).where(Alert.is_dismissed == False).order_by(desc(Alert.created_at))

    if type:
        query = query.where(Alert.type == type)
    if severity:
        query = query.where(Alert.severity == severity)
    if is_read is not None:
        query = query.where(Alert.is_read == is_read)

    result = await db.execute(query.limit(limit))
    alerts = result.scalars().all()

    equip_result = await db.execute(select(Equipment))
    equip_map = {eq.id: eq.name for eq in equip_result.scalars().all()}

    return [
        {
            "id": a.id,
            "type": a.type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "equipment_id": a.equipment_id,
            "equipment_name": equip_map.get(a.equipment_id) if a.equipment_id else None,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
            "status": getattr(a, "status", "pending"),
            "priority": getattr(a, "priority", "medium"),
            "assigned_to": getattr(a, "assigned_to", None),
        }
        for a in alerts
    ]


@router.get("/count")
async def get_alert_counts(db: AsyncSession = Depends(get_db)):
    """Get alert count summary."""
    res_total = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_dismissed == False)
    )
    total_val = res_total.scalar_one()

    res_unread = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_read == False, Alert.is_dismissed == False)
    )
    unread_val = res_unread.scalar_one()

    res_critical = await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "critical", Alert.is_dismissed == False)
    )
    critical_val = res_critical.scalar_one()

    res_warning = await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "warning", Alert.is_dismissed == False)
    )
    warning_val = res_warning.scalar_one()

    res_info = await db.execute(
        select(func.count(Alert.id)).where(Alert.severity == "info", Alert.is_dismissed == False)
    )
    info_val = res_info.scalar_one()

    return {
        "total": total_val,
        "unread": unread_val,
        "critical": critical_val,
        "warning": warning_val,
        "info": info_val,
    }


@router.patch("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Mark an alert as read."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    alert.is_read = True
    await db.flush()
    return {"id": alert_id, "status": "read"}


@router.patch("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Mark all alerts as read."""
    await db.execute(update(Alert).where(Alert.is_read == False).values(is_read=True))
    await db.flush()
    return {"status": "all_read"}


@router.patch("/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Dismiss an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    alert.is_dismissed = True
    await db.flush()
    return {"id": alert_id, "status": "dismissed"}


class ManualAlertRequest(BaseModel):
    title: str
    message: str
    equipment_id: Optional[int] = None
    priority: str = "medium"

class ResolveAlertRequest(BaseModel):
    resolution: str
    repair_duration_minutes: int
    follow_up_required: bool = False
    parts_replaced: Optional[str] = None
    cost: Optional[float] = None

@router.get("/my-jobs")
async def get_my_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Alert).where(Alert.assigned_to == current_user.id).order_by(desc(Alert.created_at))
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    equip_result = await db.execute(select(Equipment))
    equip_map = {eq.id: eq.name for eq in equip_result.scalars().all()}
    
    return [
        {
            "id": a.id,
            "type": a.type,
            "priority": a.priority,
            "status": a.status,
            "title": a.title,
            "message": a.message,
            "equipment_id": a.equipment_id,
            "equipment_name": equip_map.get(a.equipment_id) if a.equipment_id else None,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "accepted_at": a.accepted_at.isoformat() if a.accepted_at else None,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        }
        for a in alerts
    ]

@router.patch("/{alert_id}/accept")
async def accept_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    if alert.status not in ["pending", "accepted"]:
        return {"error": f"Cannot accept alert with status {alert.status}"}
    
    alert.assigned_to = current_user.id
    alert.status = "accepted"
    alert.accepted_at = datetime.utcnow()
    await db.commit()
    return {"id": alert_id, "status": "accepted"}

@router.patch("/{alert_id}/start")
async def start_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    if alert.assigned_to != current_user.id:
        return {"error": "Alert not assigned to you"}
        
    alert.status = "in_progress"
    alert.started_at = datetime.utcnow()
    await db.commit()
    return {"id": alert_id, "status": "in_progress"}

@router.patch("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    request: ResolveAlertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    if alert.assigned_to != current_user.id:
        return {"error": "Alert not assigned to you"}
        
    alert.status = "resolved"
    alert.completed_at = datetime.utcnow()
    
    # Create MaintenanceLog
    if alert.equipment_id:
        log = MaintenanceLog(
            equipment_id=alert.equipment_id,
            maintenance_type="corrective",
            performed_at=alert.started_at or datetime.utcnow(),
            completed_at=alert.completed_at,
            technician=f"{current_user.first_name} {current_user.last_name}",
            description=alert.message,
            resolution=request.resolution,
            repair_duration_minutes=request.repair_duration_minutes,
            follow_up_required=request.follow_up_required,
            parts_replaced=request.parts_replaced,
            cost=request.cost
        )
        db.add(log)
        
    await db.commit()
    return {"id": alert_id, "status": "resolved"}

@router.patch("/{alert_id}/verify")
async def verify_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"error": "Alert not found"}
    
    alert.status = "verified"
    alert.verified_at = datetime.utcnow()
    await db.commit()
    return {"id": alert_id, "status": "verified"}

@router.post("/manual")
async def create_manual_alert(
    request: ManualAlertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = Alert(
        type="maintenance",
        severity=request.priority,
        priority=request.priority,
        title=request.title,
        message=request.message,
        equipment_id=request.equipment_id,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return {"id": alert.id, "status": "pending"}
