# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import aio_pika


class RabbitMQConsumer(aio_pika.RobustConnection):
    """RabbitMQ消费者
    """

    def __init__(self, url, **kwargs):

        super().__init__(url, **kwargs)

        self._channel = None
        self._queue = None

    async def initialize(self, name, consume_qos=1):

        await self.connect()
        await self.ready()

        self._channel = await self.channel()
        await self._channel.set_qos(prefetch_count=consume_qos)

        self._queue = await self._channel.declare_queue(name)

    async def release(self):

        await self._channel.close()
        await super().close()

    async def get(self, *, no_ack=False, timeout=1):

        await self._queue.get(no_ack=no_ack, timeout=timeout)

    async def consume(self, consume_func, *, no_ack=False):

        await self._queue.consume(consume_func, no_ack=no_ack)


class RabbitMQConsumerForExchange(RabbitMQConsumer):
    """RabbitMQ自动注册到交换机的唯一消费者
    """

    async def initialize(self, name, consume_qos=1, *, routing_key=None):

        await self.connect()
        await self.ready()

        self._channel = await self.channel()
        await self._channel.set_qos(prefetch_count=consume_qos)

        self._queue = await self._channel.declare_queue(exclusive=True)

        await self._queue.bind(
            await self._channel.get_exchange(name),
            routing_key
        )
