#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-09-06 17:48:59
# @Author  : wangmian05
# @Link    : wangmian05@countrygraden.com.cn
# @Version : $Id$
import base64
import os
import sys

sys.path.append("../..")

from wmfwk.util import logger as log

config = {}


def start_with(cont, param):
    cont = cont.lstrip()
    if param in cont and (cont.index(param) == 0 or cont.index(param) == 1):
        return True
    return False


env = sys.argv[1] if len(sys.argv) > 1 else None
service_port = sys.argv[2] if len(sys.argv) > 2 else 0

log.debug("current env:{},service_port:{}", env, service_port)

env_prefix = env if env and len(env) > 0 else "local"

log.debug("profile:{}", env_prefix)
current_path = os.path.abspath(__file__)

father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

ph = str(father_path)
pwd = ph if ph.rindex("aisr-carbarn-ai") == 0 else ph[0:
                                                      (ph.index("aisr-carbarn-ai") + len("aisr-carbarn-ai"))]


if env_prefix != "local":
    pwd = pwd + "/aisr-carbarn-ai"

pwd = sys.path[0]
case_file_path = pwd + "/server-" + env_prefix + ".conf"
with open(case_file_path, "rb") as fs:
    for f in fs:
        content = f.decode('utf-8').replace("\r", '').replace("\n", '')
        if len(content) == 0 or start_with(content, "#"):
            continue

        ct_idx = content.index("=")
        isp = [content[0:ct_idx], content[ct_idx + 1:]]
        dbc = isp[1]
        if isp[0].find("passwd") >= 0:
            try:
                encrypt_code = base64.decodebytes(dbc[1:len(dbc) - 1].encode("utf-8")).decode()
                isp[1] = "".join(list(base64.decodebytes(
                    "".join(list(encrypt_code)[::-1])[len(env_prefix) + 6:len(encrypt_code)].encode("utf-8")).decode())[
                                 ::-1])
            except Exception as e:
                log.warning("config read fail...")
        config[isp[0]] = isp[1]

if __name__ == "__main__":
    con = "bgy2020"
    xxx = base64.encodebytes("".join(list(con)[::-1]).encode("utf-8")).decode()
    prefix = "uatpasswd"
    con = prefix.upper() + xxx
    xxx = base64.encodebytes("".join(list(con)[::-1]).encode("utf-8")).decode()
    print(xxx)
    ddd = base64.decodebytes(xxx.encode("utf-8")).decode()
    ccc = "".join(
        list(base64.decodebytes("".join(list(ddd)[::-1])[len(prefix):len(ddd)].encode("utf-8")).decode())[::-1])
    print(ccc)
    pass
