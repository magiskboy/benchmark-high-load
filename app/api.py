from typing import cast
from contextlib import asynccontextmanager

import aio_pika
import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, Request, Response
from fastapi.datastructures import State

from .service import (
    create_person,
    get_db_pool,
    get_rb_connection,
    get_redis_pool,
    CreatePersonBody,
    CreatePersonResponse,
)


@asynccontextmanager
async def lifespan(*_):
    db_pool = await get_db_pool()

    async with db_pool.acquire() as conn:
        conn = cast(asyncpg.Connection, conn)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS person (
                id TEXT PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                age INTEGER
            );
        ''')

    redis_client = get_redis_pool()

    rb_conn = await get_rb_connection()
    rb_channel = await rb_conn.channel()
    await rb_channel.declare_queue('tasks')

    yield {
        "pool": db_pool,
        "redis_client": redis_client,
        "rb_channel": rb_channel,
    }

    await db_pool.close()
    await redis_client.close()
    await rb_channel.close()
    await rb_conn.close()


app = FastAPI(
    lifespan=lifespan,
)


@app.post("/write", response_model=CreatePersonResponse)
async def write(body: CreatePersonBody, r: Request):
    pool = cast(State, r.state.pool)
    async with pool.acquire() as conn:
        result = await create_person(body, conn)

    return result


@app.post("/write-redis", response_model=CreatePersonBody)
async def write_redis(body: CreatePersonBody, r: Request):
    redis_client = cast(redis.Redis, r.state.redis_client)
    await redis_client.lpush('tasks', body.model_dump_json()) #type:ignore
    return Response('ok')


@app.post("/write-rabbitmq")
async def write_rabbitmq(body: CreatePersonBody, r: Request):
    channel = cast(aio_pika.abc.AbstractChannel, r.state.rb_channel)
    exchange = await channel.get_exchange('amq.direct')
    await exchange.publish(
        message=aio_pika.Message(body.model_dump_json().encode('utf-8')),
        routing_key='normal',
    )

    return Response("ok")

