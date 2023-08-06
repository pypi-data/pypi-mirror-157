import time

from wmfwk.util import logger as log


def Log(fn):
    """异步执行方法"""

    def wrapper(*args, **kwargs):
        log.info("{}方法开始执行", fn.__name__)
        method_start = time.time()
        res = fn(*args, **kwargs)
        method_end = time.time()
        methodTime = round(method_end - method_start, 2)
        log.info("{}方法执行完成,总耗时:[{}]秒...", fn.__name__, methodTime)
        return res

    return wrapper
