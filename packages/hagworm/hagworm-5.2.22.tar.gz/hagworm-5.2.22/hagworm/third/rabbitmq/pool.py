# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import aio_pika

from ...extend.asyncio.task import IntervalTask


class RabbitMQPool:
    """RabbitMQPool连接池
    """

    def __init__(self, url, pool_size, **kwargs):

        self._mq_url = url
        self._mq_setting = kwargs

        self._pool_size = pool_size

        self._connection_pool = aio_pika.pool.Pool(self._create_connection, max_size=pool_size)
        self._channel_pool = aio_pika.pool.Pool(self._create_channel, max_size=pool_size)

    async def _create_connection(self):

        return await aio_pika.connect_robust(self._mq_url, **self._mq_setting)

    async def _create_channel(self):

        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    async def close(self):

        await self._channel_pool.close()
        await self._connection_pool.close()

    def acquire_connection(self):

        return self._connection_pool.acquire()

    def acquire_channel(self):

        return self._channel_pool.acquire()


class RabbitMQProducer(RabbitMQPool):
    """RabbitMQ发布者
    """

    async def publish(self, message, routing_key, **kwargs):

        async with self.acquire_channel() as channel:
            await channel.default_exchange.publish(aio_pika.Message(message), routing_key, **kwargs)

    async def batch_publish(self, messages, routing_key, **kwargs):

        async with self.acquire_channel() as channel:
            for message in messages:
                await channel.default_exchange.publish(aio_pika.Message(message), routing_key, **kwargs)


class RabbitMQConsumer(RabbitMQPool):
    """RabbitMQ消费者
    """

    def __init__(self, url, pool_size, **kwargs):

        super().__init__(url, pool_size, **kwargs)

        self._queue_name = None
        self._consume_func = None
        self._consume_qos = None

        self._task = IntervalTask.create(10, self._consume_message)

    async def open(self, queue_name, consume_func, consume_qos=10):

        self._queue_name = queue_name
        self._consume_func = consume_func
        self._consume_qos = consume_qos

        self._task.start()

    async def close(self):

        self._task.stop()

        await super().close()

    async def _consume_message(self):

        async with self.acquire_channel() as channel:

            await channel.set_qos(self._consume_qos)

            queue = await channel.declare_queue(self._queue_name)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self._consume_func(message)
                    await message.ack()
