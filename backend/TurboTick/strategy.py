# TurboTick/strategy.py
import time
from TurboTick.state import market_data, market_depth, log_queue, current_position, WEIGHTS, data_lock
from TurboTick.logger import trade_logger

# CONFIGURATION
MOMENTUM_THRESHOLD = 0.001  # Sensitivity (Needs tuning via backtesting)
TARGET_PROFIT = 2.0        # Points
STOP_LOSS = 1.0            # Points

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

def execute_mock_trade(action, symbol, price):

    if action == "BUY":
        current_position["active"] = True
        current_position["symbol"] = symbol
        current_position["entry_price"] = price
        current_position["type"] = "CE" if "CE" in symbol else "PE"
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # LOGS TO FILE INSTANTLY
        trade_logger.info(f"🔵 ENTRY | {action} {symbol} | Price: {price}")
        
    elif action == "SELL":
        entry = current_position["entry_price"]
        pnl = price - entry
        pnl *= 25  # Lot size
        current_position["active"] = False
        current_position["symbol"] = None
        current_position["entry_price"] = 0.0
        # <>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        icon = "✅" if pnl > 0 else "❌"
        trade_logger.info(f"{icon} EXIT  | {symbol} | Price: {price} | PnL: {pnl:.2f}")


def run_strategy(ce_symbol, pe_symbol):
     # <>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    trade_logger.info(f"--- 🚀 STRATEGY STARTED: {ce_symbol} & {pe_symbol} ---")
    trade_logger.info("🧪 SYSTEM CHECK: This log confirms 'trades.log' is writable.")
    
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
            entry = current_position["entry_price"]
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

