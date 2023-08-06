# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import aio_pika


class RabbitMQProducer:
    """RabbitMQ通用发布者
    """

    def __init__(self, url, pool_size, **kwargs):

        self._mq_url = url
        self._mq_setting = kwargs

        self._connection_pool = aio_pika.pool.Pool(self._create_connection, max_size=pool_size)
        self._channel_pool = aio_pika.pool.Pool(self._create_channel, max_size=pool_size)

    async def _create_connection(self):

        return await aio_pika.connect_robust(self._mq_url, **self._mq_setting)

    async def _create_channel(self):

        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    async def release(self):

        await self._channel_pool.close()
        await self._connection_pool.close()

    def acquire_connection(self):

        return self._connection_pool.acquire()

    def acquire_channel(self):

        return self._channel_pool.acquire()

    async def publish(self, message, routing_key, **kwargs):

        async with self.acquire_channel() as channel:
            await channel.default_exchange.publish(aio_pika.Message(message), routing_key, **kwargs)

    async def batch_publish(self, messages, routing_key, **kwargs):

        async with self.acquire_channel() as channel:
            for message in messages:
                await channel.default_exchange.publish(aio_pika.Message(message), routing_key, **kwargs)


class RabbitMQProducerForExchange(RabbitMQProducer):
    """RabbitMQ使用交换机发布
    """

    def __init__(self, url, name, pool_size, **kwargs):

        super().__init__(url, pool_size, **kwargs)

        self._exchange_name = name

        self._exchange_pool = aio_pika.pool.Pool(self._create_exchange, max_size=pool_size)

    async def _create_exchange(self):

        async with self.acquire_channel() as channel:
            return await channel.get_exchange(self._exchange_name)

    def acquire_exchange(self):

        return self._exchange_pool.acquire()

    async def publish(self, message, routing_key=r'', **kwargs):

        async with self.acquire_exchange() as exchange:
            await exchange.publish(aio_pika.Message(message), routing_key, **kwargs)

    async def batch_publish(self, messages, routing_key=r'', **kwargs):

        async with self.acquire_exchange() as exchange:
            for message in messages:
                await exchange.publish(aio_pika.Message(message), routing_key, **kwargs)
