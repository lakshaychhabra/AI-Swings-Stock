from loguru import logger
import sys
from datetime import datetime
from typing import Dict, Any

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    "logs/trades.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
    rotation="1 day",
    retention="30 days",
    compression="zip"
)
logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

def log_trade(
    action: str,
    symbol: str,
    quantity: float,
    price: float,
    total_value: float,
    portfolio_state: Dict[str, Any]
) -> None:
    """
    Log trade details and portfolio state
    """
    logger.info(
        "TRADE | Action: {action} | Symbol: {symbol} | "
        "Quantity: {quantity:.2f} | Price: ${price:.2f} | "
        "Total Value: ${total_value:.2f}",
        action=action,
        symbol=symbol,
        quantity=quantity,
        price=price,
        total_value=total_value
    )
    
    logger.debug(
        "Portfolio State After Trade: {portfolio_state}",
        portfolio_state=portfolio_state
    )

def log_error(error_msg: str, context: Dict[str, Any]) -> None:
    """
    Log error messages with context
    """
    logger.error(
        "ERROR | {error_msg} | Context: {context}",
        error_msg=error_msg,
        context=context
    ) 