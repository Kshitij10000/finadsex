from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
import redis
from core.user import access_token
import json
import threading
import time
# Connect to Redis running in Docker
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


fyers_socket = None

def get_options_symbols(current_price):
    atm_strike = round(current_price / 100) * 100
    ce_symbol = f'NSE:BANKNIFTY25DEC{atm_strike}CE'
    pe_symbol = f'NSE:BANKNIFTY25DEC{atm_strike}PE'
    return ce_symbol, pe_symbol

def on_depth_update(ticker, message):
    
    try:
        # create clean dict payload from fyers object
        # Record the time the message arrived locally (server system time in seconds float)
        script_arrival_time = time.time()

        # Normalize message timestamp from fyers. The SDK may provide seconds or milliseconds.
        fyers_timestamp = None
        try:
            fyers_timestamp = float(getattr(message, 'timestamp', None))
            # If timestamp looks like milliseconds (large number) convert to seconds
            if fyers_timestamp and fyers_timestamp > 1e12:
                fyers_timestamp = fyers_timestamp / 1000.0
        except Exception:
            # If SDK uses dict-like message, try index access
            try:
                fyers_timestamp = float(message['timestamp'])
                if fyers_timestamp and fyers_timestamp > 1e12:
                    fyers_timestamp = fyers_timestamp / 1000.0
            except Exception:
                fyers_timestamp = None
        payload = {
            "symbol": ticker,
            "timestamp": message.timestamp,
            "tbq": message.tbq,  # Total Buy Qty
            "tsq": message.tsq,  # Total Sell Qty
            "bids": message.bidprice, # List of 50 bid prices
            "asks": message.askprice, # List of 50 ask prices
            "bid_qty": message.bidqty,
            "ask_qty": message.askqty,
            "script_arrival_time": script_arrival_time,
            "fyers_timestamp": fyers_timestamp
        }
        # seialize to json string (like redis needs srting)
        # Add a timestamp that marks when we publish to Redis (this helps measure system->redis latency)
        redis_publish_time = time.time()
        payload["redis_publish_time"] = redis_publish_time

        # Serialize to json string (Redis pub/sub expects a string payload)
        json_payload = json.dumps(payload)

        # publish for realtime UI (fire-and-forget)
        r.publish("channel:live_feed", json_payload)

        # push to stream for strategy (persistence/history)
        # Strategies read from stream "stream:ticks"
        # We push a dictionary where the key is 'data' and value is the JSON string
        # The returned stream id can be used as a reference for later latency checks
        stream_id = r.xadd("stream:ticks", {"data": json_payload}, maxlen=10000)

        # Optional debug logs: compute some immediate latencies (if fyers timestamp exists)
        try:
            if fyers_timestamp:
                fyers_to_system = script_arrival_time - fyers_timestamp
            else:
                fyers_to_system = None
            system_to_redis = redis_publish_time - script_arrival_time
            # print debug for observability - remove or route to proper logging in prod
            print(f"tick {ticker} id={stream_id} fyers_to_system={fyers_to_system:.6f if fyers_to_system is not None else 'N/A'}s system_to_redis={system_to_redis:.6f}s")
        except Exception:
            # keep ingestion tolerant
            pass
    except Exception as e:
        print(f"Error pushing to Redis: {e}")


def onopen():
    print("Connection opened")

    # Dynamic Symbol Selection Logic
    current_bank_nifty_price = 59850 # Ideally fetch this live via API once before starting
    BankNiftyFutures = 'NSE:BANKNIFTY25DECFUT'
    ce, pe = get_options_symbols(current_bank_nifty_price)
    
    symbols = [BankNiftyFutures, ce, pe]
    print(f"Subscribing to: {symbols}")
    # Subscription
    fyers_socket.subscribe(
        symbol_tickers=symbols, 
        channelNo='1', 
        mode=SubscriptionModes.DEPTH
    )
    fyers_socket.switchChannel(resume_channels=['1'], pause_channels=[])

    # Keep the socket running to receive real-time data
    fyers_socket.keep_running()

def onerror(message):
    """
    Callback function to handle WebSocket errors.

    Parameters:
        message (dict): The error message received from the WebSocket.

    """
    print("Error:", message)


def onclose(message):
    """
    Callback function to handle WebSocket connection close events.
    """
    print("Connection closed:", message)

def onerror_message(message):
    """
    Callback function for error message events from the server

    Parameters:
        message (dict): The error message received from the Server.

    """
    print("Error Message:", message)


def start_socket_process():

    global fyers_socket
    fyers_socket = FyersTbtSocket(
        access_token=access_token,  # Your access token for authenticating with the Fyers API.
        write_to_file=False,        # A boolean flag indicating whether to write data to a log file or not.
        log_path="",                # The path to the log file if write_to_file is set to True (empty string means current directory).
        on_open=onopen,          # Callback function to be executed upon successful WebSocket connection.
        on_close=onclose,           # Callback function to be executed when the WebSocket connection is closed.
        on_error=onerror,           # Callback function to handle any WebSocket errors that may occur.
        on_depth_update=on_depth_update, # Callback function to handle depth-related events from the WebSocket
        on_error_message=onerror_message         # Callback function to handle server-related erros from the WebSocket.
    )
    
    # Establish a connection to the Fyers WebSocket
    fyers_socket.connect()

    
    # Auto-stop after 60 seconds
    def stop_after_delay(seconds):
        threading.Timer(seconds, lambda: fyers_socket.close_connection()).start()

    stop_after_delay(600)