"""AI Assistant API router — Groq LLM integration."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.equipment import Equipment
from app.services.groq_service import groq_service
from app.schemas.analytics import ChatRequest, ChatResponse

from app.core.permissions import get_current_user
from app.models.user import User
from app.models.alert import Alert

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


@router.get("/status")
async def get_ai_status():
    """Check if AI assistant is configured and available."""
    return {
        "available": groq_service.is_available,
        "model": groq_service.model,
    }


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to the AI assistant."""
    if not request.context:
        request.context = {}
    request.context.update({
        "User": f"{current_user.first_name} {current_user.last_name}",
        "Role": current_user.role,
        "Department": current_user.department or "Unknown"
    })
    
    # Add Executive Context for Admins
    if current_user.role in ["admin", "manager"]:
        from app.models.equipment import Equipment
        from app.models.inventory import InventoryItem
        
        eq_res = await db.execute(select(Equipment.status, func.count(Equipment.id)).group_by(Equipment.status))
        request.context["Equipment_Status_Summary"] = ", ".join([f"{count} {status}" for status, count in eq_res.all()])
        
        inv_res = await db.execute(select(func.count(InventoryItem.id)).where(InventoryItem.current_stock <= InventoryItem.min_stock))
        low_stock_count = inv_res.scalar_one()
        request.context["Low_Stock_Inventory_Items"] = low_stock_count
    
    # Add Maintenance Context
    if current_user.role == "employee":
        query = select(Alert).where(Alert.assigned_to == current_user.id, Alert.status.in_(["pending", "accepted", "in_progress"]))
        res = await db.execute(query)
        jobs = res.scalars().all()
        request.context["My_Active_Jobs"] = f"{len(jobs)} active jobs"
        if jobs:
            request.context["Job_Details"] = ", ".join([f"Alert {j.id}: {j.title} ({j.status})" for j in jobs])
    
    result = await groq_service.chat(request.message, request.context)
    return result


@router.post("/analyze/{equipment_id}")
async def analyze_equipment(equipment_id: int, db: AsyncSession = Depends(get_db)):
    """Get AI analysis for specific equipment."""
    from app.models.equipment import SensorReading
    from sqlalchemy import desc

    equip_result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equip = equip_result.scalar_one_or_none()
    if not equip:
        return {"error": "Equipment not found"}

    readings_result = await db.execute(
        select(SensorReading)
        .where(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(1)
    )
    reading = readings_result.scalar_one_or_none()

    sensor_data = {
        "equipment_name": equip.name,
        "equipment_type": equip.type,
        "health_score": equip.health_score,
        "temperature": reading.temperature if reading else "N/A",
        "vibration": reading.vibration if reading else "N/A",
        "pressure": reading.pressure if reading else "N/A",
        "power_consumption": reading.power_consumption if reading else "N/A",
    }

    analysis = await groq_service.analyze_anomaly(sensor_data)
    return {"equipment_id": equipment_id, "analysis": analysis}


@router.get("/insights")
async def get_auto_insights(db: AsyncSession = Depends(get_db)):
    """Get auto-generated dashboard insights."""
    # Gather context
    equip_result = await db.execute(select(Equipment))
    equipment = equip_result.scalars().all()

    critical = [eq for eq in equipment if eq.status == "critical"]
    warning = [eq for eq in equipment if eq.status == "warning"]
    avg_health = sum(eq.health_score for eq in equipment) / max(len(equipment), 1)

    context = {
        "total_equipment": len(equipment),
        "critical_equipment": len(critical),
        "warning_equipment": len(warning),
        "avg_health_score": round(avg_health, 1),
    }

    if critical:
        context["critical_names"] = ", ".join(eq.name for eq in critical[:3])

    result = await groq_service.chat(
        "Based on the current dashboard data, provide 3-4 key insights and recommendations. "
        "Be specific about equipment names and actionable steps.",
        context
    )
    return result
