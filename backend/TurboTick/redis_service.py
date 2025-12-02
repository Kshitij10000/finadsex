import redis

# Connect to Redis running in Docker
r = redis.Redis(host="localhost", port=6379, db=0)
