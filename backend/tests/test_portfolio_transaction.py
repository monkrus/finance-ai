import pytest
from datetime import datetime
from app.models.portfolio import Portfolio, Holding, Transaction
from app.schemas.portfolio import TransactionCreate
from app.portfolio.transaction import TransactionEngine
from app.core.exceptions import FinPilotException

@pytest.mark.asyncio
async def test_process_transaction_buy(db_session, test_user):
    portfolio = Portfolio(user_id=test_user.id, name="Test Portfolio")
    db_session.add(portfolio)
    await db_session.commit()
    
    engine = TransactionEngine()
    
    tx_data = TransactionCreate(
        transaction_type="BUY",
        execution_date=datetime.utcnow(),
        ticker_symbol="AAPL",
        quantity=10,
        price_per_unit=150.0,
        fees=5.0
    )
    
    tx = await engine.process_transaction(db_session, portfolio.id, tx_data)
    
    assert tx.transaction_type == "BUY"
    assert tx.quantity == 10
    assert tx.total_amount == (10 * 150) + 5
    
    await db_session.refresh(portfolio, ["holdings"])
    holding = portfolio.holdings[0]
    assert holding.quantity == 10
    assert holding.cost_basis == 1505.0
    assert holding.average_buy_price == 150.5

@pytest.mark.asyncio
async def test_process_transaction_sell(db_session, test_user):
    portfolio = Portfolio(user_id=test_user.id, name="Test Portfolio")
    db_session.add(portfolio)
    await db_session.flush()
    
    holding = Holding(portfolio_id=portfolio.id, ticker_symbol="MSFT", quantity=20, average_buy_price=200, cost_basis=4000)
    db_session.add(holding)
    await db_session.commit()
    
    engine = TransactionEngine()
    
    tx_data = TransactionCreate(
        transaction_type="SELL",
        execution_date=datetime.utcnow(),
        holding_id=holding.id,
        quantity=5,
        price_per_unit=300.0,
        fees=10.0
    )
    
    tx = await engine.process_transaction(db_session, portfolio.id, tx_data)
    
    await db_session.refresh(holding)
    assert holding.quantity == 15
    assert holding.cost_basis == 3000.0
    assert holding.realized_gain_loss == (5 * 300 - 10) - 1000

@pytest.mark.asyncio
async def test_process_transaction_insufficient_quantity(db_session, test_user):
    portfolio = Portfolio(user_id=test_user.id, name="Test")
    db_session.add(portfolio)
    await db_session.flush()
    
    holding = Holding(portfolio_id=portfolio.id, ticker_symbol="MSFT", quantity=2, average_buy_price=200, cost_basis=400)
    db_session.add(holding)
    await db_session.commit()
    
    engine = TransactionEngine()
    
    tx_data = TransactionCreate(
        transaction_type="SELL",
        execution_date=datetime.utcnow(),
        holding_id=holding.id,
        quantity=5,
        price_per_unit=300.0
    )
    
    with pytest.raises(FinPilotException) as exc:
        await engine.process_transaction(db_session, portfolio.id, tx_data)
        
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_process_transaction_edge_cases(db_session, test_user):
    engine = TransactionEngine()
    
    # 404 Portfolio
    tx_data = TransactionCreate(transaction_type="BUY", execution_date=datetime.utcnow(), ticker_symbol="X", quantity=1, price_per_unit=1)
    with pytest.raises(FinPilotException) as exc:
        await engine.process_transaction(db_session, 9999, tx_data)
    assert exc.value.status_code == 404
    
    portfolio = Portfolio(user_id=test_user.id, name="Test Edge")
    db_session.add(portfolio)
    await db_session.flush()
    
    # Bad quantity
    tx_data.quantity = 0
    with pytest.raises(FinPilotException):
        await engine.process_transaction(db_session, portfolio.id, tx_data)
        
    # Bad price
    tx_data.quantity = 1
    tx_data.price_per_unit = -10
    with pytest.raises(FinPilotException):
        await engine.process_transaction(db_session, portfolio.id, tx_data)
        
    # Dividend
    tx_data = TransactionCreate(transaction_type="DIVIDEND", execution_date=datetime.utcnow(), ticker_symbol="X", quantity=0, price_per_unit=100)
    tx = await engine.process_transaction(db_session, portfolio.id, tx_data)
    assert tx.transaction_type == "DIVIDEND"
    
    # Sell exactly all to hit zero quantity
    holding = Holding(portfolio_id=portfolio.id, ticker_symbol="Y", quantity=10, average_buy_price=10, cost_basis=100)
    db_session.add(holding)
    await db_session.flush()
    
    tx_data = TransactionCreate(transaction_type="SELL", execution_date=datetime.utcnow(), holding_id=holding.id, quantity=10, price_per_unit=15)
    await engine.process_transaction(db_session, portfolio.id, tx_data)
    
    await db_session.refresh(holding)
    assert holding.quantity == 0
    assert holding.cost_basis == 0
    assert holding.average_buy_price == 0
