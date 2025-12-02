from fyers_apiv3.FyersWebsocket import data_ws


def onmessage(message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.

    Parameters:
        message (dict): The received message from the WebSocket.

    """
    print("Response:", message)


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


def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.

    """
    # Specify the data type and symbols you want to subscribe to
    data_type = "SymbolUpdate"

    # Subscribe to the specified symbols and data type
    symbols = ['NSE:SBIN-EQ', 'NSE:ADANIENT-EQ','NSE:RELIANCE-EQ',
               'NSE:HDFCBANK-EQ','NSE:INFY-EQ','NSE:TCS-EQ',
               'NSE:ICICIBANK-EQ','NSE:KOTAKBANK-EQ','NSE:LT-EQ',
               'NSE:HINDUNILVR-EQ','NSE:ITC-EQ','NSE:TCS-EQ',
               'NSE:BHARTIARTL-EQ','NSE:SBILIFE-EQ','NSE:AXISBANK-EQ',
               'NSE:BAJAJFINSV-EQ','NSE:BANKNIFTY25DEC59800CE','NSE:BANKNIFTY25DEC5900CE','NSE:BANKNIFTY25DEC59800PE']
    
    fyers.subscribe(symbols=symbols, data_type=data_type)

    # Keep the socket running to receive real-time data
    fyers.keep_running()


# Replace the sample access token with your actual access token obtained from Fyers
from TurboTick.config import ACCESS_TOKEN
access_token = ACCESS_TOKEN

# Create a FyersDataSocket instance with the provided parameters
fyers = data_ws.FyersDataSocket(
    access_token=access_token,       # Access token in the format "appid:accesstoken"
    log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=True,                  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,              # Save response in a log file instead of printing it.
    reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,               # Callback function to subscribe to data upon connection.
    on_close=onclose,                # Callback function to handle WebSocket connection close events.
    on_error=onerror,                # Callback function to handle WebSocket errors.
    on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
)

# Establish a connection to the Fyers WebSocket
fyers.connect()

#   ------------------------------------------------------------------------------------------------------------------------------------------
#  Sample Success Response 
#  ------------------------------------------------------------------------------------------------------------------------------------------
           
#   {
#     "ltp":606.4,
#     "vol_traded_today":3045212,
#     "last_traded_time":1690953622,
#     "exch_feed_time":1690953622,
#     "bid_size":2081,
#     "ask_size":903,
#     "bid_price":606.4,
#     "ask_price":606.45,
#     "last_traded_qty":5,
#     "tot_buy_qty":749960,
#     "tot_sell_qty":1092063,
#     "avg_trade_price":608.2,
#     "low_price":605.85,
#     "high_price":610.5,
#     "open_price":609.85,
#     "prev_close_price":620.2,
#     "type":"sf",
#     "symbol":"NSE:SBIN-EQ",
#     "ch":-13.8,
#     "chp":-2.23
#   }
import threading
# Auto-stop after 60 seconds
def stop_after_delay(seconds):
    threading.Timer(seconds, lambda: fyers.close_connection()).start()

stop_after_delay(600)  # Stop after 60 seconds