import redis
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def get_cached_user(username: str):
    user_data = redis_client.get(f"user:{username}")
    if user_data:
        return json.loads(user_data)
    return None

def set_cached_user(username: str, user_dict: dict, expire: int = 1800):
    redis_client.set(f"user:{username}", json.dumps(user_dict), ex=expire)