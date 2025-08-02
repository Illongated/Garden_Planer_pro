from datetime import timedelta
import redis.asyncio as redis

class RedisService:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def add_jti_to_denylist(self, jti: str, expires_in: timedelta):
        """
        Adds a JTI to the Redis denylist with a specified expiration time.
        The key is the JTI itself, and the value is a placeholder.
        """
        await self.redis_client.setex(f"denylist:{jti}", expires_in, "revoked")

    async def is_jti_in_denylist(self, jti: str) -> bool:
        """
        Checks if a JTI is in the Redis denylist.
        """
        return await self.redis_client.exists(f"denylist:{jti}") == 1

# Note: A dependency injection system would be ideal here to provide the
# RedisService instance to the parts of the app that need it.
# For simplicity in this context, we might instantiate it where needed,
# passing the `request.app.state.redis` client.
