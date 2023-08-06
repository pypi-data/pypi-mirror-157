#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-12-21 15:52:46
# @Author  : wangmian05
# @Link    : wangmian05@countrygraden.com.cn
# @Version : $Id$
import io
import json
import traceback

"""地库统一异常对象"""


class IParkException(Exception):
    code = 0000
    msg = None

    def __init__(self, msg, code=0000):
        super().__init__(self, msg)
        self.code = code
        self.msg = msg

    def __str__(self):
        return self.msg
