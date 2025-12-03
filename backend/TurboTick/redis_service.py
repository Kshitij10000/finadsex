import json
import time
import redis
from TurboTick.state import market_data, market_depth,current_position, WEIGHTS, data_lock

# Connect to Redis running in Docker
r = redis.Redis(host="localhost", port=6379, db=0)

def sync_state_to_redis():
    """
    Periodically sync the in-memory state to Redis for persistence and external access.
    """
    while True:
        snapshot = {}
        with data_lock:
            snapshot['market_data'] = market_data.copy()
            snapshot['market_depth'] = market_depth.copy()
            snapshot['current_position'] = current_position.copy()
        
        r.set("system_state", json.dumps(snapshot))

        time.sleep(1)  # Sync every second
