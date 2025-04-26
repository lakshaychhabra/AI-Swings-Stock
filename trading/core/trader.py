from datetime import datetime
from typing import Dict, Optional
from ..models.portfolio import Portfolio, Transaction
from ..services.redis_service import RedisService
from loguru import logger

class Trader:
    def __init__(self, initial_balance: float = 100000.0):
        self.redis_service = RedisService()
        
        # Try to load existing portfolio from Redis
        self.portfolio = self.redis_service.load_portfolio()
        if not self.portfolio:
            self.portfolio = Portfolio(cash_balance=initial_balance)
            self.redis_service.save_portfolio(self.portfolio)

    def buy(self, symbol: str, quantity: float, price: float) -> bool:
        """
        Execute a buy order
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares to buy
            price: Price per share
            
        Returns:
            bool: True if transaction successful, False otherwise
        """
        total_value = quantity * price
        
        if total_value > self.portfolio.cash_balance:
            logger.error(f"Insufficient funds for purchase: {total_value} > {self.portfolio.cash_balance}")
            return False
        
        transaction = Transaction(
            symbol=symbol,
            transaction_type="BUY",
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            total_value=total_value
        )
        
        # Update portfolio
        self.portfolio.cash_balance -= total_value
        self.portfolio.update_position(transaction)
        
        # Save to Redis
        self.redis_service.save_portfolio(self.portfolio)
        self.redis_service.save_transaction(transaction)
        
        logger.info(f"Buy order executed: {symbol}, {quantity} shares at ${price}")
        return True

    def sell(self, symbol: str, quantity: float, price: float) -> bool:
        """
        Execute a sell order
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares to sell
            price: Price per share
            
        Returns:
            bool: True if transaction successful, False otherwise
        """
        if symbol not in self.portfolio.positions:
            logger.error(f"Position not found: {symbol}")
            return False
            
        position = self.portfolio.positions[symbol]
        if position.quantity < quantity:
            logger.error(f"Insufficient shares for sale: {quantity} > {position.quantity}")
            return False
            
        total_value = quantity * price
        transaction = Transaction(
            symbol=symbol,
            transaction_type="SELL",
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            total_value=total_value
        )
        
        # Update portfolio
        self.portfolio.cash_balance += total_value
        self.portfolio.update_position(transaction)
        
        # Save to Redis
        self.redis_service.save_portfolio(self.portfolio)
        self.redis_service.save_transaction(transaction)
        
        logger.info(f"Sell order executed: {symbol}, {quantity} shares at ${price}")
        return True

    def hold(self, symbol: str) -> None:
        """
        Log a hold decision
        
        Args:
            symbol: Stock symbol
        """
        position = self.portfolio.positions.get(symbol)
        position_data = {
            "quantity": position.quantity,
            "avg_price": position.avg_price,
            "total_investment": position.total_investment
        } if position else None
        
        logger.info(f"Hold decision: {symbol}, position: {position_data}")

    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get current position for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with position details or None if position doesn't exist
        """
        position = self.portfolio.positions.get(symbol)
        if position:
            return {
                "quantity": position.quantity,
                "avg_price": position.avg_price,
                "total_investment": position.total_investment
            }
        return None

    def get_transaction_history(self) -> list:
        """Get all transaction history"""
        return self.redis_service.get_transaction_history()

    def reset_portfolio(self, initial_balance: float = 100000.0) -> None:
        """Reset the portfolio to initial state"""
        self.redis_service.flush_db()
        self.portfolio = Portfolio(cash_balance=initial_balance)
        self.redis_service.save_portfolio(self.portfolio) 