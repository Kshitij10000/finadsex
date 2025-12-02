# TurboTick/main.py
import threading
import time
from TurboTick.fyers_std_connector import fyers_standard_connection
from TurboTick.fyers_tbt_connector import fyers_tbt_connection
from TurboTick.strategy import run_strategy
from TurboTick.fyers_tbt_connector import ce, pe

if __name__ == "__main__":
    
    # 1. Start Sockets (Background)
    t1 = threading.Thread(target=fyers_standard_connection, daemon=True)
    t1.start()
    
    t2 = threading.Thread(target=fyers_tbt_connection, daemon=True)
    t2.start()
    
    # 2. Start Strategy (Background)
    t_strat = threading.Thread(target=run_strategy, args=(ce, pe), daemon=True)
    t_strat.start()
    
