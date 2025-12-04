# TurboTick/strategy.py
import time
from TurboTick.state import market_data, market_depth, log_queue, current_position, WEIGHTS, data_lock, Order , positions
import redis
import json

# redis client for storing orders
r = redis.Redis(host="localhost", port=6379, db=0)

# CONFIGURATION
MOMENTUM_THRESHOLD = 0.01  # Sensitivity (Needs tuning via backtesting)
TARGET_PROFIT = 5.0        # Points
STOP_LOSS = 2.0            # Points

# Brokerage Calculator for Fyers 
def calculate_trade_cost(buy_price,sell_price,quantity):
    
    BROKERAGE_PER_ORDER = 20.0    # Broker per order Rate
    STT_RATE = 0.001              # Security Transaction Tax , Only on sell side (0.1%)      # tumari ka ma ki chut, me q du etna paisa, modiji
    EXCHANGE_TXN_RATE = 0.0004403 # Exchange Txn Rate (NSE Options)
    IPFT_RATE = 0.000005          # Investor Protection Fund Trust (NSE IPFT)                # me q du in bhadwo ke liye paise..............
    STAMP_DUTY_RATE = 0.00003     # Stamp Duty (Buy Side Only, 0.003%)                       # Online transcation me kaika stamp duty mkc
    SEBI_FEE_RATE = 0.000001      # SEBI Turnover Fee (0.0001%)                              # kuch kam nahi karti bus paise leti hai 
    GST_RATE = 0.18               # GST (18%)                                                # q hon yeeeeeee , har cheeez me gst mkc
    # Turnover
    buy_turnover = buy_price * quantity
    sell_turnover = sell_price * quantity
    total_turnover = buy_turnover + sell_turnover
    # Brokerage (flat 20 per leg. net 40)
    brokerage = 40.0
    # STT
    stt = sell_turnover * STT_RATE
    # Exchange Transcation Charges
    etc = total_turnover * EXCHANGE_TXN_RATE
    # NSE IPFT
    ipft = total_turnover*IPFT_RATE
    # Stamp Duty
    stamp_duty = buy_turnover * STAMP_DUTY_RATE
    # SEBI Turnover Fees
    sebi_fees = total_turnover * SEBI_FEE_RATE
    # GST
    taxable_amount = brokerage + etc + sebi_fees
    gst = taxable_amount * GST_RATE
    
    # Total Taxes
    total_charges = brokerage + stt + etc + ipft + stamp_duty + sebi_fees + gst

    # PnL Calculation
    gross_pnl = (sell_price - buy_price) * quantity
    net_pnl = gross_pnl - total_charges

    return {
        "gross_pnl": round(gross_pnl,2),
        "total_charges": round(total_charges,2),
        "net_pnl": round(net_pnl, 2)
    }

def calculate_synthetic_velocity(snapshot, prev_snapshot):
    """
    Calculate the synthetic velocity of the index based on the weights of its components.
    return Float (Positive = Bullish, Negative = Bearish)
    """

    velocity = 0.0
    active_weights = 0.0

    for symbol, weight in WEIGHTS.items():
        curr = snapshot.get(symbol, 0)
        prev = prev_snapshot.get(symbol, 0)
        
        # If data is misiing or havent chnaged , skip
        if curr == 0 or prev == 0:
            continue
        
        # % Change of this stock
        pct_change = ((curr - prev) / prev) * 100

        # weighted impact
        velocity += weight * pct_change
        active_weights += weight
    
    return velocity

def close_position(symbol, exit_price):
    
    entry_price = current_position['price']
    quantity = current_position['quantity']
    total_cost = calculate_trade_cost(buy_price=entry_price,sell_price=exit_price,quantity=quantity)
    
    Payload = {
        "Symbol" : symbol,
        "entry_price" : entry_price,
        "exit_price" : exit_price,
        "quantity" : quantity,
        "gross_pnl" : total_cost['gross_pnl'],
        "total_charges" : total_cost['total_charges'],
        "net_pnl" : total_cost['net_pnl']
    }
    positions.append(Payload)
    current_position.update({
            "active": False,
            "symbol": None,
            "entry_price": 0.0,
            "quantity": 0,
            "type": "SELL"
        })



def execute_mock_trade(action, symbol, price):

    order_id = f"{int(time.time() * 1000)}"
    order = Order(order_id, symbol, price, 100, "BUY", time.time())
    if action == "BUY":
        current_position.update({
            "active": True,
            "symbol": symbol,
            "price": price,
            "quantity": 100,
            "type": "BUY"
        })
        
    elif action == "SELL":
        close_position(symbol,price)

    r.rpush("executed_orders", json.dumps(order.to_dict()))



def run_strategy(ce_symbol, pe_symbol):
    
    print("🚀 STRATEGY STARTED: {ce_symbol} & {pe_symbol}")
    print("--------------------------------")
    print("--------------------------------")
    
    prev_prices = market_data.copy()
    
    while True:
        current_prices = market_data.copy()
        
        # 2. CALCULATE MOMENTUM
        momentum = calculate_synthetic_velocity(current_prices, prev_prices)
        
        ce_ltp = 0.0
        pe_ltp = 0.0
        
        # 3. GET OPTION PRICES (FIXED)
        with data_lock:
            if ce_symbol in market_depth:
                depth = market_depth[ce_symbol]
                # Check if 'asks' list exists and is not empty
                if depth.get('asks') and len(depth['asks']) > 0:
                    # FIX: Directly access index 0. It is already a float.
                    ce_ltp = float(depth['asks'][0]) 

            if pe_symbol in market_depth:
                depth = market_depth[pe_symbol]
                if depth.get('asks') and len(depth['asks']) > 0:
                    # FIX: Directly access index 0.
                    pe_ltp = float(depth['asks'][0])

        # 4. TRADING LOGIC
        if not current_position["active"]:
            # BULLISH SIGNAL
            if momentum > MOMENTUM_THRESHOLD and ce_ltp > 0:
                log_queue.put(f"[SIGNAL] Bullish Surge! Momentum: {momentum:.4f}")
                execute_mock_trade("BUY", ce_symbol, ce_ltp)
                
            # BEARISH SIGNAL
            elif momentum < -MOMENTUM_THRESHOLD and pe_ltp > 0:
                log_queue.put(f"[SIGNAL] Bearish Crash! Momentum: {momentum:.4f}")
                execute_mock_trade("BUY", pe_symbol, pe_ltp)

        else:
            # EXIT LOGIC (Same as before)
            symbol = current_position["symbol"]
            entry = current_position["price"]
            current_ltp = ce_ltp if symbol == ce_symbol else pe_ltp
            
            if current_ltp > 0:
                diff = current_ltp - entry
                if diff >= TARGET_PROFIT:
                    execute_mock_trade("SELL", symbol, current_ltp)
                elif diff <= -STOP_LOSS:
                    execute_mock_trade("SELL", symbol, current_ltp)

        # 5. UPDATE STATE
        prev_prices = current_prices
        
        # Speed Control
        time.sleep(0.1)

