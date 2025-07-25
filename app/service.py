import os
import asyncpg
from uuid import uuid4
from pydantic import BaseModel, Field, UUID4
from typing import TYPE_CHECKING

import aio_pika
import redis.asyncio as redis


if TYPE_CHECKING:
    from asyncpg import Connection


class CreatePersonBody(BaseModel):
    first_name: str = Field()
    last_name: str = Field()
    age: int = Field(default=1)


class CreatePersonResponse(BaseModel):
    uuid: UUID4 = Field()


async def create_person(person: CreatePersonBody, conn: "Connection") -> CreatePersonResponse:
    uuid = uuid4()
    await conn.execute("""
        INSERT INTO person (id, first_name, last_name, age) VALUES ($1, $2, $3, $4)
    """, str(uuid), person.first_name, person.last_name, person.age)

    return CreatePersonResponse(uuid=uuid)


async def get_db_pool():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("Missing DATABASE_URL")
    db_pool = await asyncpg.create_pool(db_url)
    return db_pool


def get_redis_pool():
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise RuntimeError("Missing REDIS_URL")
    redis_pool = redis.ConnectionPool.from_url(redis_url)
    return redis.Redis.from_pool(redis_pool)


async def get_rb_connection():
    amqp_url = os.getenv("AMQP_URL")
    if not amqp_url:
        raise RuntimeError("Missing AMQP_URL")
    return await aio_pika.connect_robust(url=amqp_url)

