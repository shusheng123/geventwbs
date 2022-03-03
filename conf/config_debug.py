# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import os
import sys
from webconfig_default import *

# 服务地址
HOST = '0.0.0.0'

# 服务端口
PORT = 6200

# 协议
PROTO = 'http'

# 工作模式:  simple/gevent
# simple使用多线程模式启动server
# gevent会使用gevent方式启动server
# WORK_MODE = 'gevent'
WORK_MODE = 'simple'

# 服务名称，也是服务目录名
MYNAME = os.path.basename(HOME)
os.environ['MYNAME'] = MYNAME

# 服务名称上报时间间隔，单位秒
NAME_REPORT_TIME = 10

# 命名服务的地址
NAMECENTER = os.environ.get('NAMECENTER')

# IDC标识
IDC = os.environ.get('IDC')

# 调试模式: True/False
# 生产环境必须为False
DEBUG = False

# 日志文件配置
if DEBUG:
    LOGFILE = 'stdout'
else:
    LOGFILE = os.path.join(HOME, 'log/project.log')

REDIS_CONF = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': '',
}

SESSION_EXPIRE = 3600 * 72

# 数据库配置
DATABASE = {
}

# rpc服务地址
# 转发地址
RPC_SERVERS = {
    'user': {
        'addr': [
            {'addr': ('127.0.0.1', 7200), 'timeout': 20000, },
        ],
        'proto': 'tcp'
    },
}

# 允许传输的headers
ALLOWED_HEADERS = {
}

# 允许传输的cookies
ALLOWED_COOKIES = {
    'wx-token', 'sessionid'
}

# 转换规则
URL_CONF = {
    '/user/captcha/smscode': {
        'check': '',
        # 'method': 'captcha.smscode',
        # 'rpc': 'user',
    },
    '/user/wx/bind': {
        'check': '',
    },
    '/user/wx/login': {
        'check': '',
    },
}

# cookie
COOKIE_CONFIG = {
    'max_age': 10000,
    # 'domain': '.uyu.com',
    # 'domain': '127.0.0.1',
}
