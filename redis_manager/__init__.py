from configs import settings
from redis.asyncio import Redis

redis = Redis.from_url(str(settings.redis_url))
