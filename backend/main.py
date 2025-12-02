from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import redis 

r = redis.Redis(host="localhost", port=6379, db=0)

app = FastAPI(title="FINADSEX Backend",version="1.0.0")
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the FINADSEX Backend!"}

@app.websocket("/ws/orders")
async def orders_ws(websocket: WebSocket):
    await websocket.accept()
    last_index = 0  # track how many orders we've already sent

    while True:
        # get all orders from Redis
        raw_orders = r.lrange("executed_orders", last_index, -1)

        if raw_orders:
            for order in raw_orders:
                await websocket.send_json(json.loads(order))
            # move the index forward so we don't resend old orders
            last_index += len(raw_orders)

