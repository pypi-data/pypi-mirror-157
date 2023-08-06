#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-09-09 14:49:16
# @Author  : wangmian05 (wangmian05@countrygraden.com.cn)
# @Link    : https://git.bgy.com.cn/bu00439/aisr-carbarn-ai.git
# @Version : $Id$

import os

from threading import Thread
from time import sleep


def asyncMethod(f):
    """异步执行方法"""

    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
