from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
import redis
from core.user import access_token
import json
import threading

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
        payload = {
            "symbol": ticker,
            "timestamp": message.timestamp,
            "tbq": message.tbq,  # Total Buy Qty
            "tsq": message.tsq,  # Total Sell Qty
            "bids": message.bidprice, # List of 50 bid prices
            "asks": message.askprice, # List of 50 ask prices
            "bid_qty": message.bidqty,
            "ask_qty": message.askqty
        }
        # seialize to json string (like redis needs srting)
        json_payload = json.dumps(payload)

        # publish for relatime ui (fire and forget)
        r.publish("channel:live_feed", json_payload)

        # push to stream for strategy (peristentence/histroy)
        # Strategies read from stream "stream:ticks"
        # We push a dictionary where the key is 'data' and value is the JSON string
        r.xadd("stream:ticks", {"data": json_payload}, maxlen=10000)
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

    stop_after_delay(30)