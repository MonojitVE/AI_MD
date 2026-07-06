"""AI-Powered Report Generation API router."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
import json

from app.database import get_db
from app.models.report import Report
from app.models.user import User
from app.core.permissions import require_admin
from app.services.ai_report_service import ai_report_service
from app.logger import logger

router = APIRouter(prefix="/api/ai-reports", tags=["AI Reports"])

@router.get("")
async def list_reports(
    report_type: str = None, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List historical AI-generated reports."""
    query = select(Report).order_by(desc(Report.created_at)).limit(limit)
    if report_type:
        query = query.where(Report.report_type == report_type)
        
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "title": r.title,
            "report_type": r.report_type,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ]

@router.get("/{report_id}")
async def get_report(
    report_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get a specific AI report by ID."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "content": report.content,
        "created_at": report.created_at.isoformat()
    }

@router.post("/generate")
async def generate_report(
    report_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Manually trigger AI report generation."""
    title_map = {
        "executive": "Executive Summary",
        "maintenance": "Maintenance Overview",
        "equipment": "Equipment Health Analysis",
        "inventory": "Inventory Status"
    }
    title_prefix = title_map.get(report_type, "Generated AI Report")
    title = f"{title_prefix} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    
    # Generate synchronously
    try:
        report = await ai_report_service.generate_report(db, report_type, title)
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate AI report.")
    
    return {
        "id": report.id,
        "title": report.title,
        "status": "generated"
    }
