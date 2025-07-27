from config import settings
from redis.asyncio import Redis

redis = Redis.from_url(settings.redis_url)
