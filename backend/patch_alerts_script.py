import sys

def patch_file():
    with open("c:\\TEST_CODES\\GITHUB\\AI_MD\\backend\\app\\routers\\alerts.py", "r") as f:
        content = f.read()

    # 1. Update imports
    import_target = "from app.core.permissions import require_admin"
    import_replacement = "from app.core.permissions import require_admin, get_current_user\nfrom pydantic import BaseModel\nfrom datetime import datetime\nfrom app.models.alert import MaintenanceLog"
    content = content.replace(import_target, import_replacement)

    # 2. Update list_alerts dict return
    dict_target = """            "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
        }"""
    dict_replacement = """            "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
            "status": getattr(a, "status", "pending"),
            "priority": getattr(a, "priority", "medium"),
            "assigned_to": getattr(a, "assigned_to", None),
        }"""
    content = content.replace(dict_target, dict_replacement)

    # 3. Append the new endpoints and classes
    new_code = """

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
"""
    content += new_code

    with open("c:\\TEST_CODES\\GITHUB\\AI_MD\\backend\\app\\routers\\alerts.py", "w") as f:
        f.write(content)

    print("Patched successfully")

if __name__ == "__main__":
    patch_file()
