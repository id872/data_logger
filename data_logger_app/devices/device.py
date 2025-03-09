from time import time


def dev_read_time_decorator(read_func_decorated):
    def func_wrapper(self, *args, **kwargs):
        start = time()
        ret_val = read_func_decorated(self, *args, **kwargs)
        end = time()
        self.read_time = end - start
        return ret_val

    return func_wrapper


class BaseDevice:
    def __init__(self, dev_name, dev_id):
        self.dev_name = dev_name
        self.dev_id = dev_id
        self.read_time = None
        self.read_error_count = 0

    def get_read_time(self):
        if self.read_time is not None:
            return self.read_time
        return float("nan")

    def __str__(self):
        return (
            f"{self.dev_name} [{self.dev_id}] -> "
            f"data read time: {self.get_read_time():.2f} ms. "
            f"Read error counter: {self.read_error_count}"
        )
