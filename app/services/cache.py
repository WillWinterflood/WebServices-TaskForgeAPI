import json

from app.core.config import settings

try:
    from redis import Redis
    from redis.exceptions import RedisError
except ImportError:
    Redis = None

    class RedisError(Exception):
        pass


redis_client = None


def get_redis_client():
    global redis_client

    if not settings.redis_enabled:
        return None

    if Redis is None:
        return None

    if redis_client is None:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

    return redis_client


def get_cached_json(key):
    client = get_redis_client()
    if client is None:
        return None

    try:
        value = client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except (RedisError, ValueError, TypeError):
        return None


def set_cached_json(key, value):
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(key, settings.redis_cache_ttl_seconds, json.dumps(value))
    except (RedisError, TypeError, ValueError):
        return
