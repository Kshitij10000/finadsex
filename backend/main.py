from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fyers_services.fyers_apis import router as fyers_auth_router
import json
import redis 
from contextlib import asynccontextmanager
from fyers_services.fyers_ingestion import start_socket_process
import threading
import redis.asyncio as aioredis
import time
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("FastAPI Starting... Launching Fyers WebSocket in background thread.")
    # Create a daemon thread (Daemon means it dies when the main app dies)
    tbt_thread = threading.Thread(target=start_socket_process, daemon=True)
    tbt_thread.start()
    
    yield # The app runs here
    
    # --- SHUTDOWN LOGIC ---
    print("FastAPI Shutting down... cleaning up resources.")
    # (Optional: Logic to explicitly close socket if needed)

app = FastAPI(title="FINADSEX Backend",version="1.0.0", lifespan=lifespan)
    
@app.get("/")
def read_root():
    return {"message": "Welcome to the FINADSEX Backend!"}

app.include_router(fyers_auth_router)

@app.get("/lastest-tick")
async def get_lastest_tick():

    last_entry = r.xrevrange("stream:ticks", count=1)
    if not last_entry:
        return {"error": "No tick data available"}
    
    tick_id , tick_data = last_entry[0]
    stored = json.loads(tick_data['data'])

    # compute some latency fields if we've stored timestamps
    fyers_ts = stored.get("fyers_timestamp")
    script_arrival = stored.get("script_arrival_time")
    redis_pub = stored.get("redis_publish_time")

    latencies = {}
    try:
        if fyers_ts and script_arrival:
            latencies["fyers_to_system_s"] = script_arrival - fyers_ts
        if script_arrival and redis_pub:
            latencies["system_to_redis_s"] = redis_pub - script_arrival
    except Exception:
        pass

    return {"tick_id": tick_id, "data": stored, "latencies": latencies}

@app.router.websocket("/ws/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to WebSocket")
    r_async = aioredis.from_url("redis://localhost:6379", decode_responses=True)
    
    pubsub = r_async.pubsub()
    try:
        # Subscribe to the channel your ingestor is publishing to
        await pubsub.subscribe("channel:live_feed")

        async for message in pubsub.listen():
            # only handle actual messages
            if message["type"] == "message":
                # 'data' contains the json string from fyers
                raw = message["data"]

                # server receives it from Redis now
                server_receive_time = time.time()

                try:
                    obj = json.loads(raw)
                except Exception:
                    # send raw if we cannot parse
                    obj = {"raw": raw}

                # add server-side timing fields so client can calculate
                obj["server_receive_time"] = server_receive_time

                # Compute latencies if possible
                lat = {}
                fyers_ts = obj.get("fyers_timestamp")
                script_arrival = obj.get("script_arrival_time")
                redis_pub = obj.get("redis_publish_time")
                try:
                    if fyers_ts and script_arrival:
                        lat["fyers_to_system_s"] = script_arrival - fyers_ts
                    if script_arrival and redis_pub:
                        lat["system_to_redis_s"] = redis_pub - script_arrival
                    if redis_pub:
                        lat["redis_to_websocket_s"] = server_receive_time - redis_pub
                    if fyers_ts and server_receive_time:
                        lat["end_to_end_s"] = server_receive_time - fyers_ts
                except Exception:
                    pass

                obj["server_latencies"] = lat

                # time right before sending out to client
                obj["server_send_time"] = time.time()

                # send JSON string to client
                await websocket.send_text(json.dumps(obj))

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        # Cleanup connection when client leaves
        await pubsub.unsubscribe("channel:live_feed")
        await r_async.close()