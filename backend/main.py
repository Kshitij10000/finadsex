from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import redis
import asyncio

r = redis.Redis(host="localhost", port=6379, db=0)

app = FastAPI(title="FINADSEX Backend",version="1.0.0")
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the FINADSEX Backend!"}

@app.websocket("/ws")
async def websocket_test(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        await ws.send_text(data)

@app.websocket("/ws/orders")
async def orders_ws(websocket: WebSocket):
    await websocket.accept()
    last_index = 0  # track how many orders we've already sent
    
    try:
        while True:
            # get all orders from Redis starting from last_index
            raw_orders = r.lrange("executed_orders", last_index, -1)

            if raw_orders:
                for order in raw_orders:
                    await websocket.send_json(json.loads(order))
                # move the index forward so we don't resend old orders
                last_index += len(raw_orders)
            
            # Sleep to prevent blocking the event loop
            await asyncio.sleep(0.1)
    
    except WebSocketDisconnect:
        print("Client disconnected from /ws/orders")

@app.websocket("/ws/market_state")
async def market_state_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            raw_state = r.get("system_state")
            if raw_state:
                state = json.loads(raw_state)
                await websocket.send_json(state)
            
            # Sleep to prevent blocking the event loop
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected from /ws/market_state")