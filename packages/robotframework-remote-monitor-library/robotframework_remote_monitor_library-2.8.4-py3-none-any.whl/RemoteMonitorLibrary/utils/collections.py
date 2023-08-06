from threading import RLock
from typing import Any
from RemoteMonitorLibrary.utils.logger_helper import logger


class Empty(Exception):
    pass


class tsQueue(list):
    def __init__(self, get_limit=10):
        self._get_limit = get_limit
        self._lock = RLock()

    def put(self, item):
        with self._lock:
            super().append(item)

    def get(self) -> Any:
        with self._lock:
            try:
                logger.debug(f"Item '{id(self[0])}' dequeued")
                return super().pop(0)
            except IndexError:
                return Empty()

    def pop(self):
        raise AttributeError("Method 'pop' not allowed here; Use 'get'")

    def append(self, item) -> None:
        raise AttributeError("Method 'append' not allowed here; Use 'put'")

    def extend(self, _list):
        raise AttributeError("Method 'extend' not allowed here; Use 'put'")

    @property
    def qsize(self):
        return len(self)

    def empty(self):
        return len(self) == 0


class CacheList(list):
    def __init__(self, max_size=50):
        list.__init__(self)
        self._lock = RLock()
        self._max_size = max_size

    def append(self, item) -> None:
        with self._lock:
            while len(self) >= self._max_size:
                self.pop(0)
            super().append(item)
