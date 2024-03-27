import asyncio

import redis.asyncio as redis


async def main():
    client = redis.Redis()
    print(f"Ping successful: {await client.ping()}")
    await client.aclose()
    pass


if __name__ == "__main__":
    asyncio.run(main())
