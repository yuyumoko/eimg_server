import datetime
import os
import time
from functools import wraps
from .log import logger

import psutil

__all__ = ["fn_use_info", "async_fn_use_info"]


def size_format(size):
    if size < 1000:
        return "%i" % size + "B"
    elif 1000 <= size < 1000000:
        return "%.1f" % float(size / 1000) + "KB"
    elif 1000000 <= size < 1000000000:
        return "%.1f" % float(size / 1000000) + "MB"
    elif 1000000000 <= size < 1000000000000:
        return "%.1f" % float(size / 1000000000) + "GB"
    elif 1000000000000 <= size:
        return "%.1f" % float(size / 1000000000000) + "TB"


def second_string_time(seconds):
    if seconds < 60:
        return "%s秒" % seconds
    format_list = ["时", "分", "秒"]
    str_time = str(datetime.timedelta(seconds=seconds)).split(":")
    time_string = ""
    for n, v in zip(format_list, str_time):
        if float(v) > 0:
            time_string += v + n
    return time_string


def memory_info():
    memory_size = psutil.Process(os.getpid()).memory_info().rss
    return memory_size


def async_fn_use_info(function):
    @wraps(function)
    async def function_timer(*args, **kwargs):
        start_size = memory_info()
        t0 = time.perf_counter()
        result = await function(*args, **kwargs)
        t1 = time.perf_counter()
        end_size = memory_info()
        # start_str = size_format(start_size)
        # end_str = size_format(end_size)
        use_str = size_format(end_size - start_size)
        msg = function.__name__ + " 用时 %s " % second_string_time(t1 - t0)
        msg += "(use: %s)" % use_str
        logger.debug(msg)
        return result

    return function_timer


def fn_use_info(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        start_size = memory_info()
        t0 = time.perf_counter()
        result = function(*args, **kwargs)
        t1 = time.perf_counter()
        end_size = memory_info()
        # start_str = size_format(start_size)
        # end_str = size_format(end_size)
        use_str = size_format(end_size - start_size)
        msg = function.__name__ + " 用时 %s " % second_string_time(t1 - t0)
        msg += "(use: %s)" % use_str
        logger.debug(msg)
        return result

    return function_timer
