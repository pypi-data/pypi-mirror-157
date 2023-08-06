#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-09-14 16:30:50
# @Author  : wangmian05 (wangmian05@countrygraden.com.cn)
# @Link    : https://git.bgy.com.cn/bu00439/aisr-carbarn-ai.git
# @Version : $Id$
import json
import sys

from dataprocess.datapool.resultdata import ResultData
from wmfwk.util.mail_util import sendMail

sys.path.append("../..")
from wmfwk.util.config import config
from wmfwk.util import logger as log
from wmfwk import util as redis

from rocketmq.client import Producer

env_prefix = config.get("env") + ":" if "env" in config and len(config.get("env")) > 0 else ""

topic = {
    "aisr_carbarn_park_plan": env_prefix + "aisr_carbarn_park_plan",
    "aisr_carbarn_park_plan_recalculate": env_prefix + "aisr_carbarn_park_plan_recalculate",
}
result_status = {"success": 0, "error": 1}

mq_message_size = 0


def buildProducer():
    producer = None
    try:
        # params_dict = {"id": task_id, "json": 0}
        # 建立MQ连接，配置标签
        producer = Producer(config.get("mq.producer", "aisr-carbarn-ai"), compress_level=9,
                            max_message_size=1024 * 1024 * 4)
        producer.set_namesrv_addr(config.get("mq.addr", "10.222.86.84:9876"))
        # 修改最大消息限制为2M
        producer.set_max_message_size(1024 * 1024 * 4)
        producer.start()
        log.info("生产者启动成功......")

    except:
        log.error("rocketmq生产者启动失败...{}", sys.exc_info())
        producer.shutdown()
    return producer


def sendMsg(topic, val):
    global mq_message_size
    if not bool(topic):
        log.error("消息发送失败,topic不能为空")
        return
    if not bool(val):
        log.error("消息发送失败,消息内容不能为空")
        return
    log.info("开始往topic:[{}],推送mq消息", topic)
    # log.info("开始往topic:[{}],推送mq消息:{}", topic, val)

    count = 0
    success = False
    while not success and count < 3:
        count += 1
        producer = None
        try:
            from rocketmq.client import Message, Producer
            msg = Message(topic)
            msg.set_tags('*')
            msg.set_body(val)
            # 发送信息,暂时使用同步发送
            log.info("开始构建生产者对象......")
            producer = buildProducer()
            if producer:
                _p = json.dumps(producer.__dict__)
                log.info("生产者对象:{}......", _p)
            else:
                log.error("生成者对象为空!!!")
            log.info("mq-size:{},开始发送消息:{}......", mq_message_size, val)
            # 发送一次消息本地记录一次,当数量大于一定值后归零,这个数量会影响到消息投递的队列
            # ret = producer.send_orderly(msg, mq_message_size, retry_times=30)
            ret = producer.send_sync(msg)
            log.info("消息发送完成.....")
            mq_message_size = 0 if mq_message_size > 10000000 else mq_message_size + 1
            log.info("消息是否发送成功:{},消息id:{}", mq_message_size, ret.status, ret.msg_id)
            success = True
            producer.shutdown()
        except:
            log.error("开始第[{}]此重试...消息发送失败:{}", count, sys.exc_info())
        finally:
            if producer is not None:
                producer.shutdown()

    log.info("推送mq消息完成:{}", success)
    if not success:
        log.error("重试三次都失败...不在重新发送")
        raise Exception("mq消息发送失败,重试三次都失败")


def sendErrorToServer(task_id, project_id, msg):
    result_topic = topic.get("aisr_carbarn_park_plan")
    msg = {
        "taskId": task_id,
        "projectId": project_id,
        "status": result_status.get("error"),
        "msg": msg
    }
    sendMsg(result_topic, json.dumps(msg))
    log.info("[rocketmq]车位排布方案出错,错误消息发送成功...")


def sendResultToServer(content=ResultData):
    result_topic = topic.get("aisr_carbarn_park_plan")
    redis_key = result_topic + "_" + str(content.taskId) + "_" + str(content.plan_no)
    redis.setStr(redis_key, json.dumps(content.toJson()))
    # 推入mq的数据.java端只取非坐标类的数据.坐标类的数据通过redis获取
    msg = {
        "taskId": content.taskId,
        "projectId": content.projectId,
        "groupId": content.groupId,
        "status": result_status.get("success"),
        "outer": [],
        "buildings": [],
        "columns": [],
        "coreTube": [],
        "equipment": content.equipment,
        "parkCount": content.parkCount,
        "parks": [],
        "parkRedisKey": redis.global_key + redis_key,
        "divisionCount": content.divisionCount,
        "efficient": content.efficient,
        "outLines": [],
        "roadLines": [],
        "lastPlan": content.lastPlan,
        "spendTime": content.spendTime,
        "planCount": content.planCount,
        "objectKey": content.objectKey,
        "outLineArea": content.outLineArea,
        "outLineLength": content.outLineLength,
        "outLineArrays": [],
        "version": content.version
    }
    sendMsg(result_topic, json.dumps(msg))
    log.info("[rocketmq]车位排布方案数据消息发送成功...")


def sendTaskOverToServer(content=ResultData):
    """
    发送方案生成结束的标志消息去的到后端
    """
    result_topic = topic.get("aisr_carbarn_park_plan")
    msg = {
        "taskId": content.taskId,
        "projectId": content.projectId,
        "status": result_status.get("success"),
        "lastPlan": True,
    }
    sendMsg(result_topic, json.dumps(msg))

    log.info("[rocketmq]车位排布方案生成结束消息发送成功,内容:{}...", json.dumps(msg))


def sendRecalculateErrorToServer(recalculate, json_param, _msg, exc_mail_text):
    result_topic = topic.get("aisr_carbarn_park_plan_recalculate")
    if recalculate:
        msg = {
            "taskId": recalculate.taskId,
            "projectId": recalculate.projectId,
            "planId": recalculate.planId,
            "status": result_status.get("error"),
            "msg": _msg
        }
        sendMsg(result_topic, json.dumps(msg))
    log.info("[rocketmq]车位重新排布方案出错,错误消息发送成功...")
    # 发送邮件通知
    sendRequestDataMail(json_param, exc_mail_text)


def sendRequestDataMail(json_param, exc_mail_text=""):
    # 发送邮件通知
    try:
        log.info("开始发送错误邮件...")
        # 项目
        _pro_name = json_param.get("projectName") if json_param.get("projectName") else None
        # 创建人
        _creator = json_param.get("creator") if json_param.get("creator") else None
        sendMail(exc_mail_text, json.dumps(json_param), _project_name=_pro_name, _creator=_creator)
    except:
        log.error("邮件发送错误:{}", str(sys.exc_info()))


def sendRecalculateToServer(content=ResultData):
    result_topic = topic.get("aisr_carbarn_park_plan_recalculate")
    redis_key = result_topic + "_" + str(content.taskId) + "_" + str(content.projectId) + "_" + str(content.planId)
    redis.setStr(redis_key, json.dumps(content.toJson()))
    msg = {
        "taskId": content.taskId,
        "projectId": content.projectId,
        "planId": content.planId,
        "status": result_status.get("success"),
        "outer": [],
        "buildings": [],
        "columns": [],
        "coreTube": [],
        "parks": [],
        "equipment": content.equipment,
        "outLines": [],
        "roadLines": [],
        "parkRedisKey": redis.global_key + redis_key,
        "parkCount": content.parkCount,
        "efficient": content.efficient,
        "objectKey": content.objectKey,
        "outLineArea": content.outLineArea,
        "outLineLength": content.outLineLength,
        "outLineArrays": []
    }
    sendMsg(result_topic, json.dumps(msg))
    log.info("[rocketmq]车位排布重算数据消息发送成功...")


# def consumerMsgCallBack(msg):
#     topic = msg.topic
#     log.info(type(msg))
#     log.info("消息总内容:{}", msg)
#     _msg_id = msg.id
#     _msg_body = (msg.body).decode("utf-8")
#     log.info("当前mq监听服务,监听到有新的消息加入,topic:{},消息id:{},消息内容{}", topic, _msg_id, _msg_body)
#     return PullConsumer
#
#
# consumer = None
# try:
#     # params_dict = {"id": task_id, "json": 0}
#     # 建立MQ连接，配置标签
#     consumer = PushConsumer(config.get("mq.consumer", "aisr-carbarn-ai"))
#     consumer.set_namesrv_addr(config.get("mq.addr", "10.222.86.84:9876"))
#     consumer.subscribe(topic.get("aisr_carbarn_park_plan"), consumerMsgCallBack)
#     consumer.start()
#     log.info("消费者启动成功......")
# except Exception as e:
#     log.error("rocketmq消费者启动失败...{}", str(e))
#     producer.shutdown()

if __name__ == '__main__':
    sendMsg(topic.get("aisr_carbarn_park_plan"), "测试消息")
    # pass
