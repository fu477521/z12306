# encoding: utf8

import os
# from multiprocessing import Queue, Manager
import redis
# import logging

DEBUG = True

INIT_DONE = False

Q_NAME = 'z12306_data'
QUEUE = redis.StrictRedis(host='localhost', port=6379, db=1, password=None, max_connections=100, decode_responses=True)
# Auth settings
AUTH_UAMTK = None
AUTH_REAUTH_INTERVAL = 60 * 3  # 单位：秒

STATION_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'station_list.json')
# QUERY_LEFT_TICKET_COUNTER_FILE = '/tmp/12306-booking/left_ticket_counter'
SLEEP_INTERVAL = 0.6

COOKIES = {}
PAY_FILEPATH = './{date}-{order_no}-{bank_id}.html'
STATION_CODE_MAP = {}

# CHROME_APP_OPEN_CMD_MacOS = 'open -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome {filepath}'
# CHROME_APP_OPEN_CMD_LINUX = None    # TODO Linux Chrome 打开文件cmd
CHROME_APP_OPEN_CMD_WINDOWS = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe {filepath}'  # TODO Windows Chrome 打开文件cmd
CHROME_APP_OPEN_CMD = CHROME_APP_OPEN_CMD_WINDOWS

LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'app': {
            'format': '%(asctime)s - %(levelname)s - %(module)s::%(funcName)s:%(lineno)d - %(message)s'
        },
    },
    'filters': {
        'log_level': {
            # '()': os.path.join(os.path.dirname(__file__), '_logging.LogLevelFilter'),
            '()': 'ticket.cml12306._logging.LogLevelFilter',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO',
            'filters': ['log_level'],
        },
        'app': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'app.log',
            'formatter': 'app',
            'level': 'DEBUG',
        }
    },
    'loggers': {
        'booking': {
            'handlers': ['console', 'app'],
            'level': os.getenv('BOOKING_LOG_LEVEL', 'INFO'),
        }
    },
}


ORDER_COME_FROM_FLAG = (
    ('my_order', '全部'),
    ('my_resign', '可改签'),
    ('my_cs_resgin', '可变更到站'),
    ('my_refund', '可退款'),
)

ORDER_WHERE = (
    ('G', '未出行'),
    ('H', '历史订单'),
)

ORDER_QUERY_TYPE = (
    ('1', '按订票日期查询'),
    ('2', '按乘车日期查询'),
)

MEMBER_INFO_POINT_QUERY_TYPE = (
    ('0', '积分明细'),
    ('1', '收入明细'),
    ('2', '支出明细'),
)

SEAT_TYPE_BUSINESS_SEAT = u'商务座'
SEAT_TYPE_FIRST_SEAT = u'一等座'
SEAT_TYPE_SECONDE_SEAT = u'二等座'
SEAT_TYPE_HIGH_SLEEPER_SEAT = u'高级软卧'
SEAT_TYPE_SOFT_SLEEPER_SEAT = u'软卧'
SEAT_TYPE_MOVING_SLEEPER_SEAT = u'动卧'
SEAT_TYPE_HARD_SLEEPER_SEAT = u'硬卧'
SEAT_TYPE_SOFT_SEAT = u'软座'
SEAT_TYPE_HARD_SEAT = u'硬座'
SEAT_TYPE_NO_SEAT = u'无座'

SEAT_TYPE_CODE_MAP = [
    (SEAT_TYPE_BUSINESS_SEAT, '9'),
    (SEAT_TYPE_FIRST_SEAT, 'M'),
    (SEAT_TYPE_SECONDE_SEAT, 'O'),
    (SEAT_TYPE_HIGH_SLEEPER_SEAT, ''),  # TODO
    (SEAT_TYPE_SOFT_SLEEPER_SEAT, '4'),
    (SEAT_TYPE_MOVING_SLEEPER_SEAT, ''),
    (SEAT_TYPE_HARD_SLEEPER_SEAT, '3'),
    (SEAT_TYPE_SOFT_SEAT, '2'),
    (SEAT_TYPE_HARD_SEAT, '1'),
    (SEAT_TYPE_NO_SEAT, '1'),
]

TICKET_TYPE_ADULT = 1
TICKET_TYPE_CHILD = 2
TICKET_TYPE_STUDENT = 3
TICKET_TYPE_REMNANT_TROOP = 4
TICKET_TYPE_MAP = [
    (TICKET_TYPE_ADULT, '成人票'),
    (TICKET_TYPE_CHILD, '儿童票'),
    (TICKET_TYPE_STUDENT, '学生票'),
    (TICKET_TYPE_REMNANT_TROOP, '残军票'),
]

# 银行编码
BANK_ID_WX = '33000020'
BANK_ID_ALIPAY = '33000010'
BANK_ID_CHINA_RAILWAY = '00011001'
BANK_ID_UNIONPAY = '00011000'
BANK_ID_CMB = '03080000'
BANK_ID_PSBC = '01009999'
BANK_ID_CCB = '01050000'
BANK_ID_BOC = '01040000'
BANK_ID_ABC = '01030000'
BANK_ID_ICBC = '01020000'

BANK_ID_MAP = [
    (BANK_ID_WX, '微信'),
    (BANK_ID_ALIPAY, '支付宝'),
    (BANK_ID_CHINA_RAILWAY, '中铁银卡'),
    (BANK_ID_UNIONPAY, '中国银联'),
    (BANK_ID_CMB, '招商银行'),
    (BANK_ID_PSBC, '邮储银行'),
    (BANK_ID_CCB, '建设银行'),
    (BANK_ID_BOC, '中国银行'),
    (BANK_ID_ABC, '农业银行'),
    (BANK_ID_ICBC, '工商银行'),
]

QUERY_REMAINING_TICKET = 2
SUBMIT_ORDER = 3
PAY_ORDER = 4

BOOKING_STATUS_MAP = [
    (QUERY_REMAINING_TICKET, '查询余票'),
    (SUBMIT_ORDER, '提交订单'),
    (PAY_ORDER, '支付订单'),
]