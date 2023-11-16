# import asyncio
import json
import redis.exceptions
import redis.asyncio
from redis.asyncio.client import Redis

from unipoll_api.config import get_settings

settings = get_settings()


PUSH_NOTIFICATIONS_CHANNEL = "PUSH_NOTIFICATIONS_CHANNEL"


connection: Redis = redis.asyncio.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}",
    encoding="utf8",
    decode_responses=True,
)


async def publish_message(data: dict):
    try:
        await connection.publish(PUSH_NOTIFICATIONS_CHANNEL, json.dumps(data))
    except redis.exceptions.ConnectionError as e:
        print("Connection error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


async def listen_to_channel(user_id: str):
    # Create message listener and subscribe on the event source channel
    try:
        async with connection.pubsub() as listener:
            await listener.subscribe(PUSH_NOTIFICATIONS_CHANNEL)
            # Create a message generator
            while True:
                message = await listener.get_message()
                if message is None:
                    continue
                if message.get("type") == "message":
                    message = json.loads(message["data"])
                    # Checking, if the user is recipient of the message
                    if user_id == message.get("recipient_id"):
                        yield {"data": message}
    except redis.exceptions.ConnectionError as e:
        print("Connection error:", e)
