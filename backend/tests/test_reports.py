import pytest
from app.models.report import Report
from app.models.user import User
from app.core.permissions import require_admin
from sqlalchemy import select
from app.main import app

async def override_require_admin():
    return User(id=1, email="admin@test.com", role="admin")

app.dependency_overrides[require_admin] = override_require_admin

@pytest.mark.asyncio
async def test_get_reports_empty(async_client):
    response = await async_client.get("/api/ai-reports")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_generate_report(async_client, db_session):
    # Call the generate endpoint
    response = await async_client.post("/api/ai-reports/generate?report_type=executive")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "generated"
    assert "Executive" in data["title"]
    
    # Check DB
    res = await db_session.execute(select(Report))
    reports = res.scalars().all()
    assert len(reports) == 1
    assert reports[0].id == data["id"]
    
    # Check get by id
    response = await async_client.get(f"/api/ai-reports/{data['id']}")
    assert response.status_code == 200
    assert response.json()["content"] != ""
