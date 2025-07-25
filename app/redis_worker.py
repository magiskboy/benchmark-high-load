import asyncio
import uvloop
import asyncpg
from typing import cast

from .service import create_person, get_db_pool, get_redis_pool, CreatePersonBody


async def main():
    uvloop.install()
    print('Redis worker is running...')

    r = get_redis_pool()
    db_pool = await get_db_pool()

    try:
        async with db_pool.acquire() as db:
            db = cast(asyncpg.Connection, db)
            while True:
                records = await r.rpop('tasks', 5) #type:ignore
                if not records:
                    await asyncio.sleep(1)
                    continue

                for record in records:
                    body = CreatePersonBody.model_validate_json(record)
                    await create_person(body, db) 
    finally:
        await r.close()
        await db_pool.close()

