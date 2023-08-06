import time


class SimpleTimer:
    def __init__(self):
        self._enter_time = -1.0
        self._time_elapsed = -1.0

    def time_elapsed(self) -> float:
        assert self._enter_time > 0

        return self._time_elapsed

    def __enter__(self):
        self._enter_time = time.time()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._time_elapsed = time.time() - self._enter_time
