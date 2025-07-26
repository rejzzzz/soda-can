# utils/cache_manager.py
import redis
import json
import hashlib

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    
    def get_cache_key(self, *args):
        return hashlib.md5(str(args).encode()).hexdigest()
    
    async def get_cached_result(self, key):
        try:
            result = self.redis_client.get(key)
            return json.loads(result) if result else None
        except Exception:
            return None  # Graceful degradation
    
    async def cache_result(self, key, data, ttl=3600):
        try:
            self.redis_client.setex(key, ttl, json.dumps(data))
        except Exception:
            pass  # Continue without caching