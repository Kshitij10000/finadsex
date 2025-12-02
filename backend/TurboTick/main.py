# TurboTick/main.py
import threading
import time
from TurboTick.state import log_queue
from TurboTick.fyers_std_connector import fyers_connection
from TurboTick.fyers_tbt_connector import start_socket_process, ce, pe
from TurboTick.strategy import run_strategy
from TurboTick.logger import log_listener

def logger_worker():
    """
    Dedicated thread to print logs.
    Keeps the UI separate from the Algo.
    """
    while True:
        try:
            msg = log_queue.get()
            if msg:
                print(msg)
        except:
            pass


if __name__ == "__main__":

    log_listener.start()
    print("--- 🚀 STARTING TURBOTICK SIMULATION ---")
    print(f"Targeting: {ce} & {pe}")

    # 1. Start Logger
    t_log = threading.Thread(target=logger_worker, daemon=True)
    t_log.start()

    # 2. Start Components Data (Standard Socket)
    t_std = threading.Thread(target=fyers_connection, daemon=True)
    t_std.start()
    
    # 3. Start Options Data (TBT Socket)
    t_tbt = threading.Thread(target=start_socket_process, daemon=True)
    t_tbt.start()

    # Wait for sockets to warm up (populate market_data)
    print("Waiting 5s for buffers to fill...")
    time.sleep(5)

    # 4. Start Strategy
    try:
        run_strategy(ce, pe)
    except KeyboardInterrupt:
        print("Shutting down...")
        log_listener.stop()