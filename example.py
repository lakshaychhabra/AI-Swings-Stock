from trading.core.trader import Trader

def main():
    # Initialize trader with $100,000
    trader = Trader(initial_balance=100000.0)
    
    # Example: Buy 10 shares of AAPL at $170
    trader.buy(symbol="AAPL", quantity=10, price=170.0)
    
    # Example: Buy 5 more shares of AAPL at $175
    trader.buy(symbol="AAPL", quantity=5, price=175.0)
    
    # Example: Hold AAPL position
    trader.hold(symbol="AAPL")
    
    # Example: Sell 7 shares of AAPL at $180
    trader.sell(symbol="AAPL", quantity=7, price=180.0)
    
    # Check current position
    position = trader.get_position("AAPL")
    print(f"\nCurrent AAPL position: {position}")
    print(f"Current cash balance: ${trader.portfolio.cash_balance:.2f}")

if __name__ == "__main__":
    main() 