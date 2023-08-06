#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-09-09 14:49:16
# @Author  : wangmian05 (wangmian05@countrygraden.com.cn)
# @Link    : https://git.bgy.com.cn/bu00439/aisr-carbarn-ai.git
# @Version : $Id$

import time
from multiprocessing import Process

from wmfwk.util import logger as log

max_thread = 32


class ProcessPool:
    process_list = []
    max_process = 0

    def __init__(self, _max_process=max_thread):
        self.max_process = _max_process

    def asyncProcess(self, f, *args):
        """异步执行方法"""

        process = Process(target=f, args=args)
        process.start()
        self.process_list.append(process)
        if len(self.process_list) >= max_thread:
            # 查找运行态的线程,如果线程大于最大线程数.则停止消费队列任务,交给其他机器处理.
            run_list = [rl for rl in self.process_list if not rl._closed]
            _run_list = [rl for rl in run_list if rl.is_alive()]
            # 如果所有线程都在处理.则需要等待处理完成后继续处理
            if len(_run_list) >= max_thread:
                self.__wait_process(_run_list)
                log.info("当前线程池已经恢复空闲,开始处理任务")
            # _not_run_list = [rl for rl in run_list if rl._closed]
            # # 结束掉已经stop的进程
            # for nr in _not_run_list:
            #     nr.close()
            self.process_list = [rl for rl in run_list if not rl._closed or rl.is_alive()]

    # 进程等待主方法
    @staticmethod
    def __wait_process(_run_list):
        _run_list = [rl for rl in _run_list if not rl._closed]
        _not_run_list = [rl for rl in _run_list if not rl.is_alive()]
        while len(_not_run_list) == 0:
            log.info("当前线程池已满.等待所有线程执行完毕后再次启动")
            time.sleep(2)
            _not_run_list = [rl for rl in _run_list if not rl.is_alive()]


# 进程池对象
pool = ProcessPool()
