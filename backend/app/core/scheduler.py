"""APScheduler configuration for background tasks (Phase 4)."""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.database import AsyncSessionLocal
from app.services.ai_report_service import ai_report_service
from app.logger import logger

scheduler = AsyncIOScheduler()

async def generate_scheduled_report(report_type: str, title_prefix: str):
    """Background task to generate a report."""
    logger.info(f"Starting scheduled {report_type} report generation...")
    try:
        async with AsyncSessionLocal() as session:
            title = f"{title_prefix} Report - {datetime.utcnow().strftime('%Y-%m-%d')}"
            await ai_report_service.generate_report(session, report_type, title)
            logger.info(f"Scheduled {report_type} report generated successfully.")
    except Exception as e:
        logger.error(f"Failed to generate scheduled report: {e}")

def start_scheduler():
    """Initialize and start the scheduler."""
    if not scheduler.running:
        # Schedule Daily Executive Report at 8:00 AM UTC
        scheduler.add_job(
            generate_scheduled_report,
            CronTrigger(hour=8, minute=0),
            args=["executive", "Daily Executive"],
            id="daily_executive_report",
            replace_existing=True
        )
        
        # Schedule Weekly Maintenance Report every Monday at 7:00 AM UTC
        scheduler.add_job(
            generate_scheduled_report,
            CronTrigger(day_of_week='mon', hour=7, minute=0),
            args=["maintenance", "Weekly Maintenance"],
            id="weekly_maintenance_report",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("APScheduler started successfully.")
