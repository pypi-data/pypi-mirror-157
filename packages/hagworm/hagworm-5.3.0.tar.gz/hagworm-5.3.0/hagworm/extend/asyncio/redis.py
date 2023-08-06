# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from aredis import lock, StrictRedis, StrictRedisCluster

from .base import Utils

from ..error import catch_error
from ..interface import AsyncContextManager
from .ntp import NTPClient
from .transaction import Transaction


REDIS_ERROR_RETRY_COUNT = 0x10
REDIS_POOL_WATER_LEVEL_WARNING_LINE = 0x10


class _LockMixin(AsyncContextManager):

    __slots__ = [r'_locked']

    async def _context_release(self):

        await self.release()

    @property
    def locked(self):

        return self._locked

    async def acquire(self, blocking=None, blocking_timeout=None):

        if not self._locked:
            self._locked = await super().acquire(blocking, blocking_timeout)

        return self._locked

    async def release(self):

        if self._locked:
            await super().release()


class LuaLock(_LockMixin, lock.LuaLock):

    def __init__(self, *args, **kwargs):

        lock.LuaLock.__init__(self, *args, **kwargs)
        
        self._locked = False


class ClusterLock(_LockMixin, lock.ClusterLock):

    def __init__(self, *args, **kwargs):

        lock.ClusterLock.__init__(self, *args, **kwargs)

        self._locked = False


class _PoolMixin(AsyncContextManager):

    def __init__(self):

        self._name = Utils.uuid1()[:8]
        self._key_prefix = None

        LuaLock.register_scripts(self)

        Utils.log.info(
            f"Redis ({self._name}) initialized: {self.connection_pool.max_connections}"
        )

    async def _context_initialize(self):

        pass

    async def _context_release(self):

        pass

    def set_key_prefix(self, value):

        self._key_prefix = value

    def get_safe_key(self, key, *args, **kwargs):

        if self._key_prefix:
            _key = f'{self._key_prefix}:{key}'
        else:
            _key = key

        if args or kwargs:
            return f'{key}:{Utils.params_sign(*args, **kwargs)}'
        else:
            return _key

    def reset(self):

        self.connection_pool.disconnect()

        Utils.log.info(
            f'Redis connection pool reset: {self.connection_pool.max_connections}'
        )

    def close(self):

        self.connection_pool.disconnect()
        self.connection_pool.reset()

    def allocate_lock(self, name, *, timeout=60, blocking_timeout=0):

        return self.lock(name, timeout=timeout, blocking_timeout=blocking_timeout, lock_class=LuaLock)


class StrictRedisPool(StrictRedis, _PoolMixin):
    """StrictRedis连接管理
    """

    def __init__(self, host, port=6379, db=0, password=None, max_connections=32, **kwargs):

        StrictRedisPool.__init__(
            self,
            host, port, db,
            password=password, max_connections=max_connections,
            **kwargs
        )

        _PoolMixin.__init__(self)


class StrictRedisClusterPool(StrictRedisCluster, _PoolMixin):
    """StrictRedisCluster连接管理
    """

    def __init__(self, host=None, port=None, startup_nodes=None, password=None, max_connections=32, **kwargs):

        StrictRedisCluster.__init__(
            self,
            host, port, startup_nodes,
            password=password, max_connections=max_connections,
            **kwargs
        )

        _PoolMixin.__init__(self)

    def allocate_cluster_lock(self, name, *, timeout=60, blocking_timeout=0):

        return self.lock(name, timeout=timeout, blocking_timeout=blocking_timeout, lock_class=ClusterLock)


class RedisDelegate:
    """Redis功能组件
    """

    def __init__(self):

        self._redis_pool = None

    @property
    def redis_pool(self):

        return self._redis_pool

    def init_redis_single(self, host, port=6379, db=0, password=None, max_connections=32, **kwargs):

        self._redis_pool = StrictRedisPool(
            host, port, db,
            password=password, max_connections=max_connections,
            **kwargs
        )

        return self._redis_pool

    def init_redis_cluster(self, host=None, port=None, startup_nodes=None, password=None, max_connections=32, **kwargs):

        self._redis_pool = StrictRedisClusterPool(
            host, port, startup_nodes,
            password=password, max_connections=max_connections,
            **kwargs
        )

        return self._redis_pool

    def set_redis_key_prefix(self, value):

        self._redis_pool.set_key_prefix(value)

    async def redis_health(self):

        result = False

        with catch_error():
            result = bool(await self._redis_pool.info())

        return result

    def reset_redis_pool(self):

        self._redis_pool.reset()

    def close_redis_pool(self):

        self._redis_pool.close()

    def get_redis_client(self):

        return self._redis_pool


class ShareCache(AsyncContextManager):
    """共享缓存，使用with进行上下文管理

    基于分布式锁实现的一个缓存共享逻辑，保证在分布式环境下，同一时刻业务逻辑只执行一次，其运行结果会通过缓存被共享

    """

    def __init__(self, redis_client, share_key):

        self._redis_client = redis_client
        self._share_key = redis_client.get_safe_key(share_key)

        self._locker = self._redis_client.lock(
            redis_client.get_safe_key(f'share_cache:{share_key}')
        )

        self.result = None

    async def _context_release(self):

        await self.release()

    async def get(self):

        result = await self._redis_client.get(self._share_key)

        if result is None:

            locked = await self._locker.acquire()

            if not locked:
                await self._locker.wait()
                result = await self._redis_client.get(self._share_key)

        return result

    async def set(self, value, expire=0):

        result = await self._redis_client.set(self._share_key, value, expire)

        return result

    async def release(self):

        if self._locker:
            await self._locker.release()

        self._redis_client = self._locker = None


class PeriodCounter:

    MIN_EXPIRE = 60

    def __init__(self, redis_pool, time_slice: int, key_prefix: str = r'', ntp_client: NTPClient = None):

        self._redis_pool = redis_pool

        self._time_slice = time_slice
        self._key_prefix = key_prefix

        self._ntp_client = ntp_client

    def _get_key(self, key: str = None) -> str:

        timestamp = Utils.timestamp() if self._ntp_client is None else self._ntp_client.timestamp

        time_period = Utils.math.floor(timestamp / self._time_slice)

        if key is None:
            return f'{self._key_prefix}:{time_period}'
        else:
            return f'{self._key_prefix}:{key}:{time_period}'

    async def _incr(self, key: int, val: str) -> int:

        res = None

        with catch_error():
            pipeline = self._redis_pool.pipeline()
            pipeline.incrby(key, val)
            pipeline.expire(key, max(self._time_slice, self.MIN_EXPIRE))
            res, _ = await pipeline.execute()

        return res

    async def _decr(self, key: int, val: str) -> int:

        res = None

        with catch_error():
            pipeline = self._redis_pool.pipeline()
            pipeline.decrby(key, val)
            pipeline.expire(key, max(self._time_slice, self.MIN_EXPIRE))
            res, _ = await pipeline.execute()

        return res

    async def incr(self, val: int, key: str = None):

        _key = self._get_key(key)

        res = await self.incr(_key, val)

        return res

    async def incr_with_trx(self, val: int, key: str = None) -> (int, Transaction):

        _key = self._get_key(key)

        res = await self.incr(_key, val)

        if res is not None:
            trx = Transaction()
            trx.add_rollback_callback(self._decr, _key, val)
        else:
            trx = None

        return res, trx

    async def decr(self, val: int, key: str = None) -> int:

        _key = self._get_key(key)

        res = await self.decr(_key, val)

        return res

    async def decr_with_trx(self, val: int, key: str = None) -> (int, Transaction):

        _key = self._get_key(key)

        res = await self.decr(_key, val)

        if res is not None:
            trx = Transaction()
            trx.add_rollback_callback(self._incr, _key, val)
        else:
            trx = None

        return res, trx
