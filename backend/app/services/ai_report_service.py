"""Service for generating AI-powered markdown reports."""

import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.equipment import Equipment
from app.models.alert import Alert, MaintenanceLog
from app.models.inventory import InventoryItem
from app.models.report import Report
from app.services.groq_service import groq_service

class AIReportService:
    async def generate_report(self, db: AsyncSession, report_type: str, title: str) -> Report:
        """Gather aggregate data and generate a markdown report via Groq LLM."""
        
        context_data = await self._gather_context(db, report_type)
        
        prompt = f"""You are an executive AI assistant for Sentry Fab Manufacturing.
Generate a comprehensive, beautifully formatted Markdown report for: {title} (Type: {report_type.upper()}).
Use the following database aggregates to build data-driven insights. Be sure to use tables, bold text, and bullet points where appropriate. DO NOT output any XML or thinking tags, just the Markdown report.

DATA CONTEXT:
{json.dumps(context_data, indent=2)}

Include these sections:
1. Executive Summary
2. Key Metrics & Trends
3. Critical Issues & Bottlenecks
4. AI Strategic Recommendations
"""

        try:
            response = groq_service.client.chat.completions.create(
                model=groq_service.model,
                messages=[
                    {"role": "system", "content": groq_service.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                max_tokens=2048,
            )
            markdown_content = response.choices[0].message.content
        except Exception as e:
            markdown_content = f"# Error generating report\n\nAI service unavailable: {str(e)}"
            
        report = Report(
            title=title,
            report_type=report_type,
            content=markdown_content
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    async def _gather_context(self, db: AsyncSession, report_type: str) -> dict:
        """Gather aggregate data based on report type."""
        context = {"timestamp": datetime.utcnow().isoformat()}
        
        if report_type in ["executive", "equipment"]:
            # Equipment stats
            eq_res = await db.execute(select(Equipment))
            equipment = eq_res.scalars().all()
            context["equipment_total"] = len(equipment)
            context["equipment_critical"] = len([e for e in equipment if e.status == "critical"])
            context["avg_health_score"] = sum(e.health_score for e in equipment) / max(len(equipment), 1)
            context["lowest_health_machines"] = [
                {"name": e.name, "score": e.health_score} 
                for e in sorted(equipment, key=lambda x: x.health_score)[:3]
            ]
            
        if report_type in ["executive", "maintenance"]:
            # Maintenance stats
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            logs_res = await db.execute(
                select(MaintenanceLog).where(MaintenanceLog.created_at >= thirty_days_ago)
            )
            logs = logs_res.scalars().all()
            context["maintenance_jobs_last_30_days"] = len(logs)
            context["total_maintenance_cost"] = sum(l.cost for l in logs if l.cost)
            context["total_repair_duration_minutes"] = sum(l.repair_duration_minutes for l in logs if l.repair_duration_minutes)
            
            alerts_res = await db.execute(select(Alert.status, func.count(Alert.id)).group_by(Alert.status))
            context["alert_status_breakdown"] = {status: count for status, count in alerts_res.all()}

        if report_type in ["executive", "inventory"]:
            # Inventory stats
            inv_res = await db.execute(select(InventoryItem))
            items = inv_res.scalars().all()
            context["total_inventory_items"] = len(items)
            context["total_inventory_value"] = sum(i.unit_cost * i.current_stock for i in items)
            context["low_stock_items"] = [
                {"name": i.name, "current": i.current_stock, "min": i.min_stock}
                for i in items if i.current_stock <= i.min_stock
            ]

        return context

ai_report_service = AIReportService()
