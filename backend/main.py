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
    return {"tick_id": tick_id, "data": json.loads(tick_data['data'])}

@app.router.websocket("/ws/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to WebSocket")
    r_async = aioredis.from_url("redis://localhost:6379", decode_responses=True)

    # Build an initial snapshot of subscribed tickers -> last-known data
    snapshot = {}
    try:
        tickers = await r_async.smembers("set:subscribed_tickers")
        if not tickers:
            # fallback: discover symbols from recent stream entries
            recent = await r_async.xrevrange("stream:ticks", count=2000)
            found = []
            for _id, data in recent:
                try:
                    d = json.loads(data.get("data", "{}"))
                    symbol = d.get("symbol") or d.get("s")
                    if symbol and symbol not in found:
                        found.append(symbol)
                except Exception:
                    continue
            tickers = list(found)
        else:
            tickers = list(tickers)

        # Try to fetch latest entry for each ticker from the recent stream
        if tickers:
            remaining = set(tickers)
            recent = await r_async.xrevrange("stream:ticks", count=5000)
            for _id, data in recent:
                if not remaining:
                    break
                try:
                    d = json.loads(data.get("data", "{}"))
                except Exception:
                    continue
                sym = d.get("symbol") or d.get("s")
                if sym and sym in remaining:
                    snapshot[sym] = {"tick_id": _id, "data": d}
                    remaining.discard(sym)

        # Send the snapshot to the client immediately
        await websocket.send_json({"type": "snapshot", "tickers": tickers, "data": snapshot, "ts": time.time()})
    except Exception as e:
        print("Error preparing snapshot:", e)

    pubsub = r_async.pubsub()
    try:
        await pubsub.subscribe("channel:live_feed")

        async for message in pubsub.listen():
            # ignore subscribe/unsubscribe control messages
            if message.get("type") != "message":
                continue

            raw = message.get("data")
            try:
                payload = json.loads(raw)
            except Exception:
                payload = raw

            # If payload contains symbol, update snapshot and notify client with per-symbol update
            symbol = None
            if isinstance(payload, dict):
                symbol = payload.get("symbol") or payload.get("s")
            if symbol:
                snapshot[symbol] = {"data": payload, "ts": time.time()}

            # send an incremental update (or the raw payload if no symbol present)
            await websocket.send_json({"type": "update", "symbol": symbol, "data": payload, "ts": time.time()})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await pubsub.unsubscribe("channel:live_feed")
        await r_async.close()