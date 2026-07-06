"""Exportable Report Generation API router (PDF / Excel).

Deliberately thin: all data comes from the existing analytics/defects/
maintenance/dashboard query functions so report numbers can never drift
from what the dashboard itself shows. This router only formats and streams.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import report_service
from app.auth_deps import require_admin

# Reuse existing route handler functions directly instead of duplicating queries.
# These are plain async functions under the hood, callable outside the request
# cycle as long as we supply their dependencies (db) ourselves.
from app.routers.analytics import get_maintenance_costs, get_oee
from app.routers.defects import list_defects, get_defect_stats
from app.routers.maintenance import get_health_scores
from app.routers.dashboard import get_dashboard_overview

router = APIRouter(prefix="/api/reports", tags=["Reports"])

PDF_MEDIA = "application/pdf"
XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _filename(prefix: str, ext: str) -> str:
    return f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}"


def _stream(buf, media_type: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        buf,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─── Maintenance Cost Report ────────────────────────────────────────

@router.get("/maintenance-costs/pdf")
async def maintenance_costs_pdf(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Download maintenance cost breakdown as a PDF."""
    data = await get_maintenance_costs(db)
    buf = report_service.maintenance_pdf(data)
    return _stream(buf, PDF_MEDIA, _filename("maintenance_costs", "pdf"))


@router.get("/maintenance-costs/excel")
async def maintenance_costs_excel(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Download maintenance cost breakdown as an Excel workbook."""
    data = await get_maintenance_costs(db)
    buf = report_service.maintenance_excel(data)
    return _stream(buf, XLSX_MEDIA, _filename("maintenance_costs", "xlsx"))


# ─── Defect Report ─────────────────────────────────────────────────

@router.get("/defects/pdf")
async def defects_pdf_report(
    limit: int = Query(default=200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Download defect stats + recent records as a PDF."""
    stats = await get_defect_stats(db)
    defect_list = await list_defects(limit=limit, db=db)
    buf = report_service.defects_pdf(stats, defect_list)
    return _stream(buf, PDF_MEDIA, _filename("defect_report", "pdf"))


@router.get("/defects/excel")
async def defects_excel_report(
    limit: int = Query(default=500, ge=1, le=2000),
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Download defect stats + full record list as an Excel workbook."""
    stats = await get_defect_stats(db)
    defect_list = await list_defects(limit=limit, db=db)
    buf = report_service.defects_excel(stats, defect_list)
    return _stream(buf, XLSX_MEDIA, _filename("defect_report", "xlsx"))


# ─── OEE Report ──────────────────────────────────────────────────────

@router.get("/oee/pdf")
async def oee_pdf_report(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Download OEE breakdown + equipment health as a PDF."""
    oee = await get_oee(db)
    health = await get_health_scores(db)
    buf = report_service.oee_pdf(oee, health)
    return _stream(buf, PDF_MEDIA, _filename("oee_report", "pdf"))


@router.get("/oee/excel")
async def oee_excel_report(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Download OEE breakdown + equipment health as an Excel workbook."""
    oee = await get_oee(db)
    health = await get_health_scores(db)
    buf = report_service.oee_excel(oee, health)
    return _stream(buf, XLSX_MEDIA, _filename("oee_report", "xlsx"))


# ─── Executive Summary (combined, client-ready) ─────────────────────

@router.get("/executive-summary/pdf")
async def executive_summary_pdf_report(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Download a single combined PDF: fleet overview, OEE, costs, defects, recent alerts."""
    overview = await get_dashboard_overview(db)
    oee = await get_oee(db)
    maintenance = await get_maintenance_costs(db)
    defect_stats = await get_defect_stats(db)
    buf = report_service.executive_summary_pdf(overview, oee, maintenance, defect_stats)
    return _stream(buf, PDF_MEDIA, _filename("executive_summary", "pdf"))