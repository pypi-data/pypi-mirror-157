# -*- coding: utf-8 -*-
# AUTHOR  : wjia
# TIME    : 2022/6/21 17:08
# FILE    : tool
# PROJECT : funfunc
# IDE     : PyCharm
import datetime
import functools
import json
import logging
import os
import time
import warnings


def get_current_str_time() -> str:
    now_time = datetime.datetime.now()
    str_time = now_time.strftime('%Y年%m月%d日星期%w %H时%M分%S秒')
    return str_time


def download_file(url, save_path):
    import requests

    r = requests.get(url, stream=True)
    with open(os.path.join(save_path), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)


def time_it(method):
    @functools.wraps(method)
    def waapper(*args, **kwargs):
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()
        print('{} USED TIME:{}'.format(method.__name__, end - start))

        return result

    return waapper


def quick_sort(arr: list) -> list:
    if len(arr) < 2:
        return arr
    temp = arr[0]
    small = [i for i in arr[1:] if i <= temp]
    big = [i for i in arr[1:] if i > temp]
    return quick_sort(small) + [temp] + quick_sort(big)


def get_basic_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(__name__)
    return logger


def chunks(arr: list, n: int) -> list:
    """将列表n等分"""
    return [arr[i:i + n] for i in range(0, len(arr), n)]


def get_host_ip():
    """查询本机ip地址"""
    import socket

    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def time_to_timestamp(date):
    """时间转化为时间戳"""
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()


def second_to_strtime(second: int):
    """秒转化为分秒"""
    return time.strftime("%M:%S", time.gmtime(second))


def set_deprecated(warn_msg=None):
    """set a function into deprecated state"""

    def outer(deprecated_func):
        def inner(*args, **kwargs):
            if warn_msg and isinstance(warn_msg, str):
                warnings.warn(warn_msg, DeprecationWarning, 2)
            else:
                warnings.warn(f"This function {deprecated_func.__name__}() is deprecated!", DeprecationWarning, 2)
            core = deprecated_func(*args, **kwargs)
            return core

        return inner

    return outer


def indented_json_string(json_string):
    return json.dumps(json_string, indent=2, ensure_ascii=False)
