import pytest
from app.models.portfolio import Portfolio

@pytest.mark.asyncio
async def test_create_portfolio(client, test_user_token_headers):
    response = await client.post(
        "/api/v1/portfolios/",
        headers=test_user_token_headers,
        json={"name": "My Retirement", "currency": "USD"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "My Retirement"
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_portfolios(client, test_user_token_headers, db_session, test_user):
    p1 = Portfolio(user_id=test_user.id, name="P1")
    db_session.add(p1)
    await db_session.commit()
    
    response = await client.get("/api/v1/portfolios/", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "P1" for p in data)

@pytest.mark.asyncio
async def test_create_transaction_api(client, test_user_token_headers, db_session, test_user):
    p = Portfolio(user_id=test_user.id, name="Test Tx API")
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)
    
    tx_data = {
        "transaction_type": "BUY",
        "execution_date": "2024-01-01T10:00:00Z",
        "ticker_symbol": "TSLA",
        "quantity": 5.0,
        "price_per_unit": 200.0,
        "fees": 2.0
    }
    
    response = await client.post(
        f"/api/v1/portfolios/{p.id}/transactions",
        headers=test_user_token_headers,
        json=tx_data
    )
    
    assert response.status_code == 201
    assert response.json()["transaction_type"] == "BUY"
    assert response.json()["total_amount"] == 1002.0
