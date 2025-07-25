import asyncio
import uvloop
import aio_pika
import asyncpg
from typing import cast

from .service import create_person, get_db_pool, get_rb_connection, CreatePersonBody


async def main():
    uvloop.install()
    print('RabbitMQ worker is running...')
    db_pool = await get_db_pool()
    rabbitmq_conn = await get_rb_connection()
    rb_channel = await rabbitmq_conn.channel()
    exchange = await rb_channel.get_exchange('amq.direct')
    queue = await rb_channel.declare_queue('tasks', durable=False)
    await queue.bind(exchange, 'normal')

    try:
        async with db_pool.acquire() as db:
            async with queue.iterator() as it:
                message: aio_pika.abc.AbstractIncomingMessage
                db = cast(asyncpg.Connection, db)
                async for message in it:
                    async with message.process():
                        body = CreatePersonBody.model_validate_json(message.body)
                        await create_person(body, db) 
    finally:
        await db_pool.close()
        await queue.unbind(exchange, 'normal')
        await rabbitmq_conn.close()

