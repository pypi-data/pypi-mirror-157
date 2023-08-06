#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-09-07 17:07:08
# @Author  : wangmian05
# @Link    : wangmian05@countrygraden.com.cn
# @Version : $Id$

import json
import multiprocessing
import sys
import threading
import time

from wmfwk.util import logger as log, rocketmq_util
from wmfwk import util as redis
import main
from wmfwk.util.exception_util import formatException
from wmfwk.util.proces_util import pool

exec_count = 0
count_lock = multiprocessing.Lock()


# # 线程主方法
# def run_task_content(content):
#     global exec_count
#     count_lock.acquire()
#     exec_count += 1
#     count_lock.release()
#     data = json.loads(content)
#     task_id = data.get("taskId")
#     time.sleep(0.5)
#     # raise Exception("throw exception...")
#     log.info("*********消费,编号:{},任务:{}执行完成...", exec_count, task_id)


def _run_task_content(content):
    data = None
    try:
        try:
            data = json.loads(content)
            task_id = data.get("taskId")
            log.info("消费队列进程开始处理任务:{}...", task_id)
            redis.runningTask(task_id)
            main.design(data)
            redis.overTaskStatus(task_id)
            log.info("消费队列进程处理完成:{}...", task_id)
        except:
            log.error("【严重】车位排布任务处理失败{}:", sys.exc_info())
            task_id = data.get("taskId")
            project_id = data.get("projectId")
            _exc_text = "【严重】车位排布任务处理失败:<br />" + formatException(sys.exc_info())
            redis.errorTaskStatus(task_id, _exc_text)
            rocketmq_util.sendErrorToServer(task_id, project_id, "【严重】车位排布任务处理过程中发生严重错误")
    except:
        log.error("【炒鸡严重】当前进程发生位置错误,导致任务不执行,请检查任务状态:{}", sys.exc_info())


# 进程管理主方法
def __handleParkTask(content):
    task_id = None
    data = None
    try:
        data = json.loads(content)
        task_id = data.get("taskId")
        log.info("出队列,编号:{},任务:{}开始运行...", exec_count, task_id)
        redis.startTask(task_id)
        pool.asyncProcess(_run_task_content, content)
        # process = Process(target=_run_task_content, args=(content,))
        # process.start()
        # process_list.append(process)
        # if len(process_list) >= max_thread:
        #     # 查找运行态的线程,如果线程大于最大线程数.则停止消费队列任务,交给其他机器处理.
        #     run_list = [rl for rl in process_list if not rl._closed]
        #     _run_list = [rl for rl in run_list if rl.is_alive()]
        #     # 如果所有线程都在处理.则需要等待处理完成后继续处理
        #     if len(_run_list) >= max_thread:
        #         __wait_process(_run_list)
        #         log.info("当前线程池已经恢复空闲,开始处理任务")
        #     # _not_run_list = [rl for rl in run_list if rl._closed or not rl.is_alive()]
        #     # # 结束掉已经stop的进程
        #     # for nr in _not_run_list:
        #     #     nr.close()
        #     process_list = [rl for rl in run_list if rl.is_alive()]
    except:
        log.error("车位排布队列发生严重异常.redis队列数据读取解析失败:{}", sys.exc_info())
        if task_id is not None:
            _exc_text = "【严重】车位排布队列发生严重异常,redis队列数据读取解析失败:<br />" + formatException(sys.exc_info())
            redis.errorTaskStatus(task_id, _exc_text)
            redis.overTaskStatus(task_id)
            project_id = data.get("projectId") if data is not None else 0
            rocketmq_util.sendErrorToServer(task_id, project_id, "【严重】车位排布任务进程池处理过程发生严重异常")


def _run_task():
    log.info("客户端消费车位排布队列任务启动完成...")
    while True:
        try:
            content = redis.bRpop(redis.carbarn_queue_key)
            global exec_count
            count_lock.acquire()
            exec_count += 1
            count_lock.release()
            log.info("监听开始,当前节点已处理:{}个任务", exec_count)
            __handleParkTask(content)
        except:
            log.debug("this rpop throw exception,retry rpop:{}", sys.exc_info())
            continue

        # 所有任务队列的时候都需要停顿500毫秒.给其他机器一点机会
        time.sleep(0.5)


# 线程启动方法
def start():
    # 此处单独开一个线程监听队列任务.不能使用进程的方式,否则会导致mq发送消息是出现发送失败
    threading.Thread(target=_run_task).start()


# 新任务处理加入队列
def pushQueue(content):
    log.info("当前有新的车位排布任务:" + str(content)[0:100])
    task_id = buildTaskId(content)
    redis.lPush(redis.carbarn_queue_key, json.dumps(content))
    redis.putTask(task_id, json.dumps(content))
    return {"taskId": task_id}


def buildTaskId(content):
    pro_id = content.get("projectId")
    worker = genid.IdWorker(1, 1, 0)
    task_id = str(pro_id) + str(worker.get_id())
    content["taskId"] = task_id
    return task_id


if __name__ == "__main__":
    pass
    start()
