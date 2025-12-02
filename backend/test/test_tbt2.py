from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
from TurboTick.config import ACCESS_TOKEN

def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.

    """
    print("Connection opened")
    # Specify the data type and symbols you want to subscribe to
    mode = SubscriptionModes.DEPTH
    Channel = '1'
    # Subscribe to the specified symbols and data type
    symbols = ['NSE:NIFTYBANK-INDEX','NSE:BANKNIFTY25DECFUT','NSE:BANKNIFTY25DEC59800CE','NSE:BANKNIFTY25DEC59800PE']
    
    
    fyers.subscribe(symbol_tickers=symbols, channelNo=Channel, mode=mode)
    fyers.switchChannel(resume_channels=[Channel], pause_channels=[])

    # Keep the socket running to receive real-time data
    fyers.keep_running()

def on_depth_update(ticker, message):
    """
    Callback function to handle incoming messages from the FyersDataSocket WebSocket.

    Parameters:
        ticker (str): The ticker symbol of the received message.
        message (Depth): The received message from the WebSocket.

    """
    print("ticker", ticker)
    print("depth response:", message)
    print("total buy qty:", message.tbq)
    print("total sell qty:", message.tsq)
    print("bids:", message.bidprice)
    print("asks:", message.askprice)
    print("bidqty:", message.bidqty)
    print("askqty:", message.askqty)
    print("bids ord numbers:", message.bidordn)
    print("asks ord numbers:", message.askordn)
    print("issnapshot:", message.snapshot)
    print("tick timestamp:", message.timestamp)


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





fyers = FyersTbtSocket(
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
fyers.connect()
import threading
# Auto-stop after 60 seconds
def stop_after_delay(seconds):
    threading.Timer(seconds, lambda: fyers.close_connection()).start()

stop_after_delay(15)  # Stop after 15 seconds