# TurboTick/state.py
import threading
import queue


# we will store the latest market data here in dictionary
# access time : ~50 nanoseconds (very fast).
# no db calls, no file i/o, just in-memory operations

# 1. In "market_data" we will store current and previous to calculate change instantly
market_data = {

    # Target Assets
    "NSE:NIFTYBANK-INDEX": 0.0, # spot index
    # Components
    "NSE:HDFCBANK-EQ": 0.0,
    "NSE:ICICIBANK-EQ": 0.0,
    "NSE:SBIN-EQ": 0.0,
    "NSE:AXISBANK-EQ": 0.0,
    "NSE:KOTAKBANK-EQ": 0.0,
    "NSE:FEDERALBNK-EQ": 0.0,
    "NSE:INDUSINDBK-EQ": 0.0,
    "NSE:AUBANK-EQ": 0.0,
    # "NSE:BANKBARODA-EQ": 0.0,
    # "NSE:CANBK-EQ": 0.0
}

# 2. Market Depth   (For Options Execution)
market_depth = {} 

# 3. Weights for each component in the index
# weights are based on market cap and top 8 stocks impact ~85%
# we will use lesser to save the CPU cylces.
WEIGHTS = {
    "NSE:HDFCBANK-EQ": 0.2765,    # 27.65%
    "NSE:ICICIBANK-EQ": 0.2300,   # 23.00%
    "NSE:SBIN-EQ": 0.0943,        # 9.43%
    "NSE:AXISBANK-EQ": 0.0910,    # 9.10%
    "NSE:KOTAKBANK-EQ": 0.0875,   # 8.75%
    "NSE:FEDERALBNK-EQ": 0.0377,  # 3.77%
    "NSE:INDUSINDBK-EQ": 0.0336,  # 3.36%
    "NSE:AUBANK-EQ": 0.0319,      # 3.19%
    # "NSE:BANKBARODA-EQ": 0.0318,  # 3.18%
    # "NSE:CANBK-EQ": 0.0304        # 3.04%
}

# 4. TRADE SIGNALS & LOGS (Decoupled from Speed)
# Strategy pushes logs here, a separate thread prints them.
log_queue = queue.Queue()


# 5. TRADING STATE
# To prevent buying 100 times in 1 second
current_position = {
    "active": False,
    "symbol": None,
    "price": 0.0,
    "quantity": 0,
    "type": None, # "BUY" or "SELL"
}

positions = []

class Order:
    __slots__ = ['order_id', 'symbol', 'price', 'qty', 'status', 'timestamp']

    def __init__(self, order_id, symbol, price, qty, status, timestamp):
        self.order_id = order_id
        self.symbol = symbol
        self.price = price
        self.qty = qty
        self.status = status
        self.timestamp = timestamp
    
    def to_dict(self):
        return {
            "order_id": self.order_id, 
            "symbol": self.symbol, 
            "price": self.price, 
            "qty": self.qty, 
            "status": self.status,
            "timestamp": self.timestamp
        }  
    
    
# global lock for thread-safe operations on market_data , cant read when writting data
data_lock = threading.Lock()