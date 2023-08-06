from queue import PriorityQueue
from threading import Thread
from typing import List, Callable

from simple_proxy2.data.observer import Observer
from simple_proxy2.data.proxy import Proxy
from simple_proxy2.data.proxy_info import ProxyInfo


class ProxyPool(Observer):
    def __init__(self,
                 success_rate_supplier: Callable[[], float],
                 proxy_infos: List[ProxyInfo]):
        self._success_rate_supplier = success_rate_supplier
        self._pool = PriorityQueue()

        self._init_proxy_thread = Thread(target=self._init_proxy, args=(proxy_infos,))
        self._init_proxy_started = False

    def _init_proxy(self, proxy_infos: List[ProxyInfo]):
        assert len(proxy_infos) > 0, "At least one proxy must exist for ProxyPool to work properly."

        for info in proxy_infos:
            if not self._init_proxy_started:
                break

            proxy = Proxy(info, self._success_rate_supplier)
            proxy.register_observer(self)
            self._pool.put(proxy)

    def poll(self) -> Proxy:
        assert self._init_proxy_started, "Proxy initialization is not started." \
                                         " Make sure to use the pool with #start()"

        return self._pool.get()

    def notify(self, proxy: Proxy):
        self._pool.put(proxy)

    def start(self):
        self._init_proxy_started = True
        self._init_proxy_thread.start()

    def end(self):
        self._init_proxy_started = False
        self._init_proxy_thread.join()

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
