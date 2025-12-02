# TurboTick/fyers_tbt_connector.py
from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
from TurboTick.config import ACCESS_TOKEN
import json
import threading
from TurboTick.state import market_depth , data_lock


fyers_tbt_socket = None
current_bank_nifty_price = 59600 # Ideally fetch this live via API once before starting


def get_options_symbols(spot_price):
    atm_strike = round(spot_price / 100) * 100
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
        with data_lock:
            market_depth[ticker] = payload
        
    except Exception as e:
        print(f"Error pushing to Redis: {e}")
        
ce, pe = get_options_symbols(current_bank_nifty_price)

def onopen():
    print("Connection opened")

    # Dynamic Symbol Selection Logic
    # Dynamic Symbol Selection Logic

    BankNiftyFutures = 'NSE:BANKNIFTY25DECFUT'
    
    
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
    print("Error:", message)


def onclose(message):
    print("Connection closed:", message)

def onerror_message(message):
    print("Error Message:", message)


def start_socket_process():

    global fyers_socket
    fyers_socket = FyersTbtSocket(
        access_token=ACCESS_TOKEN,  # Your access token for authenticating with the Fyers API.
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

    stop_after_delay(7200)

if __name__ == "__main__":
    start_socket_process()