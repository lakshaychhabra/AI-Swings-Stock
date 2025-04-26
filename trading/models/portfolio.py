from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float
    total_investment: float
    realized_pnl: float = 0.0
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.total_investment

    @property
    def unrealized_pnl_percentage(self) -> float:
        if self.total_investment == 0:
            return 0.0
        return (self.unrealized_pnl / self.total_investment) * 100

@dataclass
class Transaction:
    symbol: str
    transaction_type: str  # 'BUY' or 'SELL'
    quantity: float
    price: float
    timestamp: datetime
    total_value: float
    realized_pnl: float = 0.0

@dataclass
class Portfolio:
    cash_balance: float
    positions: Dict[str, Position] = field(default_factory=dict)
    transaction_history: List[Transaction] = field(default_factory=list)
    total_realized_pnl: float = 0.0

    def update_position(self, transaction: Transaction) -> None:
        symbol = transaction.symbol
        if transaction.transaction_type == "BUY":
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=transaction.quantity,
                    avg_price=transaction.price,
                    total_investment=transaction.total_value,
                    current_price=transaction.price
                )
            else:
                current_position = self.positions[symbol]
                new_quantity = current_position.quantity + transaction.quantity
                new_total_investment = current_position.total_investment + transaction.total_value
                new_avg_price = new_total_investment / new_quantity
                
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=new_quantity,
                    avg_price=new_avg_price,
                    total_investment=new_total_investment,
                    realized_pnl=current_position.realized_pnl,
                    current_price=transaction.price
                )
        elif transaction.transaction_type == "SELL":
            if symbol in self.positions:
                current_position = self.positions[symbol]
                new_quantity = current_position.quantity - transaction.quantity
                
                # Calculate realized PnL for this sale
                sale_pnl = (transaction.price - current_position.avg_price) * transaction.quantity
                new_realized_pnl = current_position.realized_pnl + sale_pnl
                self.total_realized_pnl += sale_pnl
                transaction.realized_pnl = sale_pnl

                if new_quantity <= 0:
                    del self.positions[symbol]
                else:
                    new_total_investment = current_position.avg_price * new_quantity
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=new_quantity,
                        avg_price=current_position.avg_price,
                        total_investment=new_total_investment,
                        realized_pnl=new_realized_pnl,
                        current_price=transaction.price
                    )

        self.transaction_history.append(transaction)

    def update_market_prices(self, price_updates: Dict[str, float]) -> None:
        """Update current market prices for positions"""
        for symbol, price in price_updates.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price

    @property
    def total_unrealized_pnl(self) -> float:
        """Calculate total unrealized PnL across all positions"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())

    @property
    def total_portfolio_value(self) -> float:
        """Calculate total portfolio value including cash and positions"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash_balance + positions_value 