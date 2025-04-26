import redis
import json
from typing import Dict, Optional
from ..models.portfolio import Portfolio, Position, Transaction
from datetime import datetime

class RedisService:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.PORTFOLIO_KEY = "trading:portfolio"
        self.TRANSACTIONS_KEY = "trading:transactions"
        self.MARKET_PRICES_KEY = "trading:market_prices"
        self.DAILY_PNL_KEY = "trading:daily_pnl"

    def save_portfolio(self, portfolio: Portfolio) -> None:
        """Save portfolio state to Redis"""
        portfolio_data = {
            "cash_balance": portfolio.cash_balance,
            "total_realized_pnl": portfolio.total_realized_pnl,
            "positions": {
                symbol: {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "total_investment": pos.total_investment,
                    "realized_pnl": pos.realized_pnl,
                    "current_price": pos.current_price
                }
                for symbol, pos in portfolio.positions.items()
            }
        }
        self.redis_client.set(self.PORTFOLIO_KEY, json.dumps(portfolio_data))

    def load_portfolio(self) -> Optional[Portfolio]:
        """Load portfolio state from Redis"""
        portfolio_data = self.redis_client.get(self.PORTFOLIO_KEY)
        if not portfolio_data:
            return None

        data = json.loads(portfolio_data)
        portfolio = Portfolio(
            cash_balance=data["cash_balance"],
            total_realized_pnl=data.get("total_realized_pnl", 0.0)
        )
        
        for symbol, pos_data in data["positions"].items():
            portfolio.positions[symbol] = Position(
                symbol=pos_data["symbol"],
                quantity=pos_data["quantity"],
                avg_price=pos_data["avg_price"],
                total_investment=pos_data["total_investment"],
                realized_pnl=pos_data.get("realized_pnl", 0.0),
                current_price=pos_data.get("current_price", pos_data["avg_price"])
            )
        
        return portfolio

    def save_transaction(self, transaction: Transaction) -> None:
        """Save transaction to Redis"""
        transaction_data = {
            "symbol": transaction.symbol,
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "timestamp": transaction.timestamp.isoformat(),
            "total_value": transaction.total_value,
            "realized_pnl": transaction.realized_pnl
        }
        
        # Get existing transactions
        transactions = self.load_transactions()
        transactions.append(transaction_data)
        
        # Save updated transactions list
        self.redis_client.set(self.TRANSACTIONS_KEY, json.dumps(transactions))

    def load_transactions(self) -> list:
        """Load all transactions from Redis"""
        transactions_data = self.redis_client.get(self.TRANSACTIONS_KEY)
        if not transactions_data:
            return []
        return json.loads(transactions_data)

    def get_transaction_history(self) -> list:
        """Get formatted transaction history"""
        transactions = self.load_transactions()
        return [
            {
                **tx,
                "timestamp": datetime.fromisoformat(tx["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            }
            for tx in transactions
        ]

    def save_market_prices(self, prices: Dict[str, float]) -> None:
        """Save current market prices"""
        self.redis_client.set(self.MARKET_PRICES_KEY, json.dumps(prices))

    def load_market_prices(self) -> Dict[str, float]:
        """Load current market prices"""
        prices_data = self.redis_client.get(self.MARKET_PRICES_KEY)
        if not prices_data:
            return {}
        return json.loads(prices_data)

    def save_daily_pnl(self, daily_pnl_data: dict) -> None:
        """Save daily PnL data to Redis"""
        today = datetime.now().strftime("%Y-%m-%d")
        current_data = self.load_daily_pnl()
        current_data[today] = daily_pnl_data
        self.redis_client.set(self.DAILY_PNL_KEY, json.dumps(current_data))

    def load_daily_pnl(self) -> Dict[str, dict]:
        """Load daily PnL data from Redis"""
        daily_pnl_data = self.redis_client.get(self.DAILY_PNL_KEY)
        if not daily_pnl_data:
            return {}
        return json.loads(daily_pnl_data)

    def get_today_pnl(self) -> dict:
        """Get PnL data for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_data = self.load_daily_pnl()
        return daily_data.get(today, {
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "total_pnl": 0.0
        })

    def flush_db(self) -> None:
        """Clear all trading related data from Redis"""
        self.redis_client.delete(self.PORTFOLIO_KEY)
        self.redis_client.delete(self.TRANSACTIONS_KEY)
        self.redis_client.delete(self.MARKET_PRICES_KEY)
        self.redis_client.delete(self.DAILY_PNL_KEY)

    def is_connected(self) -> bool:
        """Check if Redis connection is alive"""
        try:
            self.redis_client.ping()
            return True
        except redis.ConnectionError:
            return False 