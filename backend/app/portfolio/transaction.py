from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.models.portfolio import Portfolio, Holding, Transaction
from app.schemas.portfolio import TransactionCreate
from app.core.exceptions import FinPilotException

class TransactionEngine:
    async def _get_or_create_holding(self, db: AsyncSession, portfolio_id: int, ticker_symbol: str) -> Holding:
        result = await db.execute(select(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.ticker_symbol == ticker_symbol
        ))
        holding = result.scalars().first()
        
        if not holding:
            holding = Holding(
                portfolio_id=portfolio_id,
                ticker_symbol=ticker_symbol,
                quantity=0.0,
                average_buy_price=0.0,
                cost_basis=0.0,
                realized_gain_loss=0.0
            )
            db.add(holding)
            await db.flush() # Get the ID
        return holding

    async def process_transaction(self, db: AsyncSession, portfolio_id: int, tx_data: TransactionCreate) -> Transaction:
        # Validate portfolio
        result = await db.execute(select(Portfolio).filter(Portfolio.id == portfolio_id))
        portfolio = result.scalars().first()
        if not portfolio:
            raise FinPilotException(status_code=404, message="Portfolio not found")

        # Basic constraints
        if tx_data.quantity <= 0 and tx_data.transaction_type in ["BUY", "SELL"]:
            raise FinPilotException(status_code=400, message="Transaction quantity must be > 0 for BUY/SELL")
        if tx_data.price_per_unit < 0:
            raise FinPilotException(status_code=400, message="Transaction price cannot be negative")

        holding = None
        if tx_data.holding_id:
            result = await db.execute(select(Holding).filter(Holding.id == tx_data.holding_id))
            holding = result.scalars().first()
        elif tx_data.ticker_symbol:
            holding = await self._get_or_create_holding(db, portfolio_id, tx_data.ticker_symbol)

        if holding and holding.portfolio_id != portfolio_id:
            raise FinPilotException(status_code=400, message="Holding does not belong to this portfolio")
            
        # Determine total amount
        tx_val = (tx_data.quantity * tx_data.price_per_unit) + tx_data.fees + tx_data.taxes
        
        if tx_data.transaction_type == "BUY":
            if not holding:
                raise FinPilotException(status_code=400, message="BUY requires a holding")
                
            total_cost_addition = (tx_data.quantity * tx_data.price_per_unit) + tx_data.fees
            new_quantity = holding.quantity + tx_data.quantity
            new_cost_basis = holding.cost_basis + total_cost_addition
            
            holding.average_buy_price = new_cost_basis / new_quantity if new_quantity > 0 else 0
            holding.cost_basis = new_cost_basis
            holding.quantity = new_quantity

        elif tx_data.transaction_type == "SELL":
            if not holding:
                raise FinPilotException(status_code=400, message="SELL requires a holding")
            if holding.quantity < tx_data.quantity:
                raise FinPilotException(status_code=400, message="Insufficient holding quantity to sell")
                
            fraction_sold = tx_data.quantity / holding.quantity
            cost_basis_reduction = holding.cost_basis * fraction_sold
            
            proceeds = (tx_data.quantity * tx_data.price_per_unit) - tx_data.fees - tx_data.taxes
            realized_gl = proceeds - cost_basis_reduction
            
            holding.realized_gain_loss += realized_gl
            holding.quantity -= tx_data.quantity
            holding.cost_basis -= cost_basis_reduction
            
            if holding.quantity == 0:
                holding.average_buy_price = 0
                holding.cost_basis = 0
                
            tx_val = proceeds

        elif tx_data.transaction_type == "DIVIDEND":
             if holding:
                 holding.realized_gain_loss += tx_val

        transaction = Transaction(
            portfolio_id=portfolio_id,
            holding_id=holding.id if holding else None,
            transaction_type=tx_data.transaction_type,
            execution_date=tx_data.execution_date,
            quantity=tx_data.quantity,
            price_per_unit=tx_data.price_per_unit,
            fees=tx_data.fees,
            taxes=tx_data.taxes,
            total_amount=tx_val,
            currency=tx_data.currency
        )
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        
        return transaction
