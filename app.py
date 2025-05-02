from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict
import plotly.graph_objects as go
import plotly.utils
import json
import yfinance as yf
from trading.core.trader import Trader
from trading.services.redis_service import RedisService


app = FastAPI(title="Trading API")
templates = Jinja2Templates(directory="templates")

# Initialize trader with $100,000
trader = Trader(initial_balance=100000.0)
redis_service = RedisService()

# Check Redis connection
if not redis_service.is_connected():
    raise HTTPException(status_code=500, detail="Could not connect to Redis")

class TradeRequest(BaseModel):
    symbol: str
    quantity: float
    price: float

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/portfolio/viz", response_class=HTMLResponse)
async def portfolio_visualization(request: Request):
    # Calculate total portfolio value and PnL
    total_investment = sum(pos.total_investment for pos in trader.portfolio.positions.values())
    total_market_value = sum(pos.market_value for pos in trader.portfolio.positions.values())
    cash_balance = trader.portfolio.cash_balance
    total_portfolio_value = total_market_value + cash_balance
    total_unrealized_pnl = trader.portfolio.total_unrealized_pnl
    total_realized_pnl = trader.portfolio.total_realized_pnl
    total_pnl = total_unrealized_pnl + total_realized_pnl

    # Get daily PnL data
    daily_pnl = redis_service.get_today_pnl()
    
    # Save current PnL data for today
    redis_service.save_daily_pnl({
        "realized_pnl": total_realized_pnl,
        "unrealized_pnl": total_unrealized_pnl,
        "total_pnl": total_pnl
    })

    # Get transaction history
    transactions = trader.get_transaction_history()
    
    # Organize transactions by symbol
    position_transactions = {}
    for tx in transactions:
        symbol = tx["symbol"]
        if symbol not in position_transactions:
            position_transactions[symbol] = []
        position_transactions[symbol].append({
            "date": tx["timestamp"],
            "quantity": tx["quantity"],
            "price": tx["price"],
            "type": tx["transaction_type"]
        })

    # Add current price information for each position
    position_info = {
        symbol: {
            "current_price": pos.current_price,
            "avg_price": pos.avg_price,
            "quantity": pos.quantity,
            "unrealized_pnl": pos.unrealized_pnl
        }
        for symbol, pos in trader.portfolio.positions.items()
    }

    # Prepare data for allocation pie chart
    allocation_data = {
        "data": [
            {
                "labels": ["Cash"] + list(trader.portfolio.positions.keys()),
                "values": [cash_balance] + [pos.market_value for pos in trader.portfolio.positions.values()],
                "type": "pie",
                "hole": 0.4,
                "hovertemplate": "%{label}<br>$%{value:.2f}<br>%{percent}<extra></extra>"
            }
        ],
        "layout": {
            "title": "Portfolio Allocation",
            "showlegend": True,
            "height": 400
        }
    }

    # Prepare data for PnL chart
    pnl_data = {
        "data": [
            {
                "x": list(trader.portfolio.positions.keys()),
                "y": [pos.unrealized_pnl for pos in trader.portfolio.positions.values()],
                "type": "bar",
                "name": "Unrealized P&L",
                "hovertemplate": "$%{y:.2f}<extra></extra>"
            },
            {
                "x": list(trader.portfolio.positions.keys()),
                "y": [pos.realized_pnl for pos in trader.portfolio.positions.values()],
                "type": "bar",
                "name": "Realized P&L",
                "hovertemplate": "$%{y:.2f}<extra></extra>"
            }
        ],
        "layout": {
            "title": "Profit & Loss by Position",
            "barmode": "group",
            "xaxis": {"title": "Stock Symbol"},
            "yaxis": {"title": "P&L ($)"},
            "height": 400
        }
    }

    # Prepare data for position performance chart
    performance_data = {
        "data": [
            {
                "x": list(trader.portfolio.positions.keys()),
                "y": [pos.unrealized_pnl_percentage for pos in trader.portfolio.positions.values()],
                "type": "bar",
                "name": "Return %",
                "hovertemplate": "%{y:.2f}%<extra></extra>"
            }
        ],
        "layout": {
            "title": "Position Performance (%)",
            "xaxis": {"title": "Stock Symbol"},
            "yaxis": {"title": "Return (%)"},
            "height": 400
        }
    }

    return templates.TemplateResponse(
        "portfolio_viz.html",
        {
            "request": request,
            "cash_balance": cash_balance,
            "total_portfolio_value": total_portfolio_value,
            "total_investment": total_investment,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_realized_pnl": total_realized_pnl,
            "total_pnl": total_pnl,
            "daily_unrealized_pnl": daily_pnl.get("unrealized_pnl", 0.0),
            "daily_realized_pnl": daily_pnl.get("realized_pnl", 0.0),
            "daily_total_pnl": daily_pnl.get("total_pnl", 0.0),
            "allocation_chart": json.dumps(allocation_data),
            "pnl_chart": json.dumps(pnl_data),
            "performance_chart": json.dumps(performance_data),
            "position_transactions": json.dumps(position_transactions),
            "position_info": json.dumps(position_info),
            "symbols": list(trader.portfolio.positions.keys())
        }
    )

@app.post("/api/buy")
async def buy_stock(trade: TradeRequest):
    success = trader.buy(
        symbol=trade.symbol,
        quantity=trade.quantity,
        price=trade.price
    )
    return {
        "success": success,
        "message": "Purchase successful" if success else "Purchase failed"
    }

@app.post("/api/sell")
async def sell_stock(trade: TradeRequest):
    success = trader.sell(
        symbol=trade.symbol,
        quantity=trade.quantity,
        price=trade.price
    )
    return {
        "success": success,
        "message": "Sale successful" if success else "Sale failed"
    }

@app.get("/api/position/{symbol}")
async def get_position(symbol: str):
    position = trader.get_position(symbol)
    return {
        "symbol": symbol,
        "position": position
    }

@app.get("/api/portfolio")
async def get_portfolio():
    return {
        "cash_balance": trader.portfolio.cash_balance,
        "positions": {
            symbol: {
                "quantity": pos.quantity,
                "avg_price": pos.avg_price,
                "total_investment": pos.total_investment
            }
            for symbol, pos in trader.portfolio.positions.items()
        }
    }

@app.get("/api/transactions")
async def get_transactions():
    """Get all transaction history"""
    return {"transactions": trader.get_transaction_history()}

@app.post("/api/reset")
async def reset_portfolio():
    """Reset the portfolio to initial state"""
    trader.reset_portfolio()
    return {"message": "Portfolio reset successfully"}

@app.get("/api/current_prices")
async def get_current_prices():
    """Get current prices for all positions in the portfolio"""
    try:
        symbols = list(trader.portfolio.positions.keys())
        if not symbols:
            return {"prices": {}}
            
        # Fetch current prices using yfinance
        prices = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            current_price = ticker.info.get('regularMarketPrice', 0.0)
            prices[symbol] = current_price
            
            # Update position's current price
            if symbol in trader.portfolio.positions:
                trader.portfolio.positions[symbol].current_price = current_price
        
        # Calculate updated PnL values
        total_unrealized_pnl = trader.portfolio.total_unrealized_pnl
        total_realized_pnl = trader.portfolio.total_realized_pnl
        total_pnl = total_unrealized_pnl + total_realized_pnl
        
        # Get position info with updated prices
        position_info = {
            symbol: {
                "current_price": pos.current_price,
                "avg_price": pos.avg_price,
                "quantity": pos.quantity,
                "unrealized_pnl": pos.unrealized_pnl,
                "market_value": pos.market_value
            }
            for symbol, pos in trader.portfolio.positions.items()
        }
        
        return {
            "prices": prices,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_realized_pnl": total_realized_pnl,
            "total_pnl": total_pnl,
            "position_info": position_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/price/{symbol}")
async def get_current_price(symbol: str):
    """Get current price for a single symbol"""
    try:
        ticker = yf.Ticker(symbol)
        current_price = ticker.info.get('regularMarketPrice', 0.0)
        return {
            "symbol": symbol,
            "price": current_price,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cash_balance")
async def get_cash_balance():
    """Get current cash balance"""
    try:
        return {
            "cash_balance": trader.portfolio.cash_balance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_ticker(request: dict):
    ticker = request.get("ticker")
    if not ticker:
        return {"error": "Missing 'ticker'"}

    today = str(date.today())

    # Load local cache
    if os.path.exists(NEWS_PATH):
        with open(NEWS_PATH, "r") as f:
            news_data = json.load(f)
    else:
        news_data = {}

    # Run news agent if ticker missing or outdated
    if ticker not in news_data or news_data[ticker].get("date") != today:
        print("📡 Fetching fresh news...")
        articles = run_news_agent(ticker)
        news_data[ticker] = {"date": today, "articles": articles}

        with open(NEWS_PATH, "w") as f:
            json.dump(news_data, f, indent=2)
    else:
        articles = news_data[ticker]["articles"]

    news_decision = analyze_news_sentiment(ticker, articles)
    ta_decision = run_ta_agent(ticker)
    final_decision = combine_signals(news_decision, ta_decision)

    return {
        "ticker": ticker,
        "news_decision": news_decision,
        "ta_decision": ta_decision,
        "final_decision": final_decision
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 