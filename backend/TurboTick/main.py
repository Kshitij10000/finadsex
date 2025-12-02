# TurboTick/main.py
import threading
import time
import signal
import sys
from TurboTick.fyers_std_connector import fyers_standard_connection
from TurboTick.fyers_tbt_connector import fyers_tbt_connection
from TurboTick.strategy import run_strategy
from TurboTick.fyers_tbt_connector import ce, pe

stop_event = threading.Event()

def _run_with_stop(fn, *args, **kwargs):
    fn(*args, **kwargs)  # if your connectors support a stop, pass stop_event

if __name__ == "__main__":
    def handle_sigint(sig, frame):
        stop_event.set()
        print("Shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    t1 = threading.Thread(target=_run_with_stop, args=(fyers_standard_connection,), daemon=False)
    t2 = threading.Thread(target=_run_with_stop, args=(fyers_tbt_connection,), daemon=False)
    t_strat = threading.Thread(target=run_strategy, args=(ce, pe), daemon=False)

    t1.start()
    t2.start()
    t_strat.start()

    # Block main until threads exit
    t1.join()
    t2.join()
    t_strat.join()