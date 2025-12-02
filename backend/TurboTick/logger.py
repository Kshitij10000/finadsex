# TurboTick/logger.py
import logging
import logging.handlers
import queue
import sys

# 1. THE QUEUE (Buffer)
trade_log_queue = queue.Queue()

def setup_logger():
    # Create the Logger ID
    logger = logging.getLogger("TurboTickTrader")
    logger.setLevel(logging.INFO)
    
    # --- HANDLER 1: FILE (FIXED) ---
    # We added encoding='utf-8' here. This allows emojis to be saved.
    file_handler = logging.FileHandler("trades.log", mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')
    file_handler.setFormatter(formatter)
    
    # --- HANDLER 2: CONSOLE (FIXED) ---
    # Windows consoles can be tricky. We force UTF-8 here too if possible,
    # but the FileHandler was the main cause of the crash.
    console_handler = logging.StreamHandler(sys.stdout)
    try:
        console_handler.setStream(open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1))
    except:
        pass # Fallback if re-opening stdout fails
    
    console_handler.setFormatter(formatter)

    # --- THE ASYNC GLUE ---
    queue_handler = logging.handlers.QueueHandler(trade_log_queue)
    logger.addHandler(queue_handler)

    listener = logging.handlers.QueueListener(
        trade_log_queue, 
        file_handler, 
        console_handler
    )
    
    return logger, listener

# Create the instances immediately
trade_logger, log_listener = setup_logger()