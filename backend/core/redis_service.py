import redis

# Connect to Redis running in Docker
r = redis.Redis(host="localhost", port=6379, db=0)

# Quick test
r.set("foo", "bar")
print(r.get("foo"))  # b'bar'