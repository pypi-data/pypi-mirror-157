#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-12-21 15:52:46
# @Author  : wangmian05
# @Link    : wangmian05@countrygraden.com.cn
# @Version : $Id$
import io
import json
import traceback


# 外圈不成立方案排布异常
class OuterArrangeException(Exception):
    def __init__(self, msg):
        self.message = msg


def formatException(ei):
    """
    Format and return the specified exception information as a string.

    This default implementation just uses
    traceback.print_exception()
    """
    _tab = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    sio = io.StringIO()
    tb = ei[2]
    # See issues #9427, #1553375. Commented out for now.
    # if getattr(self, 'fullstack', False):
    #    traceback.print_stack(tb.tb_frame.f_back, file=sio)
    traceback.print_exception(ei[0], ei[1], tb, None, sio)
    s = sio.getvalue()
    sio.close()
    if s[-1:] == "\n":
        s = s[:-1]
    return _tab + s.replace("\n", "<br />" + _tab)
