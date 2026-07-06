import pytest

@pytest.mark.asyncio
async def test_get_equipment_empty(async_client):
    response = await async_client.get("/api/equipment")
    assert response.status_code == 200
    assert response.json() == []
