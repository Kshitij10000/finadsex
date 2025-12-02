# TurboTick/fyers_std_connector.py

from fyers_apiv3.FyersWebsocket import data_ws
from TurboTick.config import ACCESS_TOKEN
import threading
from TurboTick.state import market_data, data_lock

# Standard Fyers WebSocket instance for components market data
fyers_std_websocket = None

def onmessage(message):
    print(message)
    if isinstance(message, dict) and 'symbol' in message and 'ltp' in message:
        symbol = message['symbol']
        ltp = float(message['ltp'])
        market_data[symbol] = ltp
        


def onerror(message):
    print("Error:", message)


def onclose(message):
    print("Standard Socket closed:", message)


def onopen():
    data_type = "SymbolUpdate"
    # equity is closed for use the mcx to testing
    symbols = ['NSE:NIFTYBANK-INDEX','NSE:HDFCBANK-EQ','NSE:ICICIBANK-EQ','NSE:SBIN-EQ','NSE:KOTAKBANK-EQ','NSE:AXISBANK-EQ','NSE:FEDERALBNK-EQ','NSE:INDUSINDBK-EQ','NSE:AUBANK-EQ','NSE:BANKBARODA-EQ','NSE:CANBK-EQ']
    # symbols = ['MCX:GOLD25DECFUT','MCX:SILVER25DECFUT','MCX:CRUDEOIL25DECFUT','MCX:NATURALGAS25DECFUT','MCX:COPPER25DECFUT']
    fyers_standard_websocket.subscribe(symbols=symbols, data_type=data_type)
    fyers_standard_websocket.keep_running()


def fyers_standard_connection():

    global fyers_standard_websocket
    fyers_standard_websocket = data_ws.FyersDataSocket(
        access_token=ACCESS_TOKEN,       # Access token in the format "appid:accesstoken"
        log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
        litemode=True,                  # Lite mode disabled. Set to True if you want a lite response.
        write_to_file=True,              # Save response in a log file instead of printing it.
        reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
        on_connect=onopen,               # Callback function to subscribe to data upon connection.
        on_close=onclose,                # Callback function to handle WebSocket connection close events.
        on_error=onerror,                # Callback function to handle WebSocket errors.
        on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
    )

    # Establish a connection to the Fyers WebSocket
    fyers_standard_websocket.connect()

    # Auto-stop after 60 seconds
    def stop_after_delay(seconds):
        threading.Timer(seconds, lambda: fyers_standard_websocket.close_connection()).start()

    stop_after_delay(7200)

if __name__ == "__main__":
    fyers_standard_connection()
    
