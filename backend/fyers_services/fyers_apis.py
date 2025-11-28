# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from core.user import client_id, secret_key, redirect_uri, response_type, state, access_token
from fastapi import APIRouter , WebSocket, WebSocketDisconnect
from fyers_apiv3.FyersWebsocket.tbt_ws import FyersTbtSocket, SubscriptionModes
import asyncio


router = APIRouter(prefix="/fyers", tags=["Fyers Authentication"])

@router.get("/generate-auth-code")
def generate_fyers_auth_code():
    # Create a session model with the provided credentials
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type=response_type
    )

    # Generate the auth code using the session model
    response = session.generate_authcode()

    # Print the auth code received in the response
    return response


@router.get("/generate-access-token")
def generate_fyers_access_token(auth_code:str):

    grant_type = "authorization_code"  
    # Create a session object to handle the Fyers API authentication and token generation
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key, 
        redirect_uri=redirect_uri, 
        response_type=response_type, 
        grant_type=grant_type
    )

    # Set the authorization code in the session object
    session.set_token(auth_code)

    # Generate the access token using the authorization code
    response = session.generate_token()

    # Print the response, which should contain the access token and other details
    return response

@router.get("/callback")
def fyers_callback(auth_code: str | None = None, state: str | None = None):
    if not auth_code:
        return {"error": "missing code"}
    # Exchange the code immediately
    return generate_fyers_access_token(auth_code)

@router.get("/user-profile")
def fyers_user_profile():
    # Create a FyersModel instance with the provided access token
    fyers = fyersModel.FyersModel(client_id=client_id,is_async=False,token=access_token,log_path="")

    # Fetch the user profile using the FyersModel instance
    profile = fyers.get_profile()

    fyers_id = profile["data"]["fy_id"]
    fyers_name = profile["data"]["name"]
    return {"fyers_id": fyers_id, "fyers_name": fyers_name}

@router.get("/user-balance")
def fyers_user_balance():
    # Create a FyersModel instance with the provided access token
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")

    # Fetch the user balance using the FyersModel instance
    response = fyers.funds()

    return response['fund_limit']

@router.get("/user-holdings")
def fyers_user_holdings():
    # Create a FyersModel instance with the provided access token
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")

    # Fetch the user holdings using the FyersModel instance
    response = fyers.holdings()

    return response['holdings']

@router.websocket("/get-tbt-data")
async def fyers_get_tbt_data(websocket: WebSocket):
    await websocket.accept()
    
    fyers_socket = None
    try:
        data_queue = asyncio.Queue()

        def on_depth_update(ticker, message):
            """
            Callback to handle depth updates from Fyers.
            Puts data into a thread-safe queue.
            """
            data = {
                "type": "depthUpdate",
                "ticker": ticker,
                "tbq": message.tbq,
                "tsq": message.tsq,
                "bidprice": message.bidprice,
                "askprice": message.askprice,
                "timestamp": message.timestamp
            }
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(data_queue.put_nowait, data)
            except Exception as e:
                print(f"Error putting data in queue: {e}")

        def onerror(message):
            print(f"Fyers WebSocket Error: {message}")
            error_data = {"type": "error", "message": message}
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(data_queue.put_nowait, error_data)
            except Exception as e:
                print(f"Error putting error in queue: {e}")

        def onopen():
            """
            Callback on successful Fyers WebSocket connection.
            Subscribes to the required symbols.
            """
            print("Fyers TBT Connection opened")
            symbols = ['NSE:BANKNIFTY25DEC59800CE', 'NSE:HDFCBANK-EQ','NSE:ICICIBANK-EQ','NSE:KOTAKBANK-EQ','NSE:SBIN-EQ']
            mode = SubscriptionModes.DEPTH
            channel = '1'
            fyers_socket.subscribe(symbol_tickers=symbols, channelNo=channel, mode=mode)
            fyers_socket.switchChannel(resume_channels=[channel], pause_channels=[])
            # Keep the socket running to receive real-time data
            fyers_socket.keep_running()
       
        fyers_socket = FyersTbtSocket(
            access_token=access_token,
            write_to_file=False,
            log_path="",
            on_open=onopen,
            on_depth_update=on_depth_update,
            on_error=onerror,
        )
        
        # This starts the connection in a background thread
        fyers_socket.connect()

        # Loop to get data from the queue and send it to the client
        while True:
            data = await data_queue.get()
            await websocket.send_json(data)

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.close(code=1011, reason=str(e))
    finally:
        if fyers_socket:
            print("Closing Fyers connection.")
            fyers_socket.close_connection()