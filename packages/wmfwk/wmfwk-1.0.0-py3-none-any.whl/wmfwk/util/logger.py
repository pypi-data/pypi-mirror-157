import logging
import os
import sys
import time

# 创建日志
logging.getLogger("shapely").setLevel(logging.CRITICAL)
logger = logging.getLogger()

# 设置日志
# 等级总开关的默认级别为WARNING，此处改为DEBUG
logger.setLevel(logging.DEBUG)

env = sys.argv[1] if len(sys.argv) > 1 else None
env_prefix = env if env and len(env) > 0 else "local"
if env_prefix != "local":
    # 文件handler
    log_time = time.strftime('%Y%m%d', time.localtime(time.time()))
    log_path = os.path.join(os.getcwd(), 'logs/')
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file_name = log_path + log_time + '.log'
    file_handler = logging.FileHandler(log_file_name)
    # 设置文件handler的等级
    file_handler.setLevel(logging.ERROR)
    # 第三步，定义handler的输出格式
    file_formatter = logging.Formatter(
        "%(asctime)s - %(filename)s[line:%(lineno)d] - pid:%(process)d - tid:%(thread)d - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

# 控制台handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


def debug(msg, *args):
    pid = os.getpid()
    if msg is None:
        return
    if len(args) > 0:
        logger.debug("process [{}] :".format(pid) + str(msg).format(*args))
    else:
        logger.debug("process [{}] :".format(pid) + str(msg))


def info(msg, *args):
    if msg is None:
        return
    pid = os.getpid()
    if len(args) > 0:
        logger.info("process [{}] :".format(pid) + str(msg).format(*args))
    else:
        logger.info("process [{}] :".format(pid) + str(msg))


def warning(msg, *args):
    pid = os.getpid()
    if msg is None:
        return
    if len(args) > 0:
        logger.warning("process [{}] :".format(pid) + str(msg).format(*args))
    else:
        logger.warning("process [{}] :".format(pid) + str(msg))


def error(msg, *args):
    if msg is None:
        return
    pid = os.getpid()
    if len(args) > 0:
        pid = os.getpid()
        logger.error("process [{}] :".format(pid) + str(msg).format(*args), exc_info=True)
    else:
        logger.error("process [{}] :".format(pid) + str(msg))


# File "/data/deploy/aisr-carbarn-ai/util/logger.py", line 53, in info
#   logger.info(("process [{}] :" + msg).format(pid))

def critical(msg, *args):
    logger.critical(msg)


if __name__ == "__main__":
    debug('this is a logger debug message{}')
    info('this is a logger info message,{}', 233)
    warning('this is a logger warning message:', 12)
    error('this is a logger error message')
    critical('this is a logger critical message')
