import sys
sys.path.append('../')
sys.path.append('../../')
import os
import re
import time
import json
import logging
# import platform
import logging.config

from ticket.cml12306 import configs
from ticket.cml12306 import exceptions
from .query import query_left_tickets
from .auth import auth_is_login, auth_reauth, auth_qr
from .order import order_check_no_complete, order_submit
from .user import user_passengers


_logger = logging.getLogger('booking')

__all__ = ('initialize', 'run')

def initialize():
    """
    Initialization.
    """
    if configs.INIT_DONE:  # INIT_DONE = False
        return

    # station_list = []
    station_code_map = {}
    with open(configs.STATION_LIST_FILE, 'r', encoding='utf-8') as f:   # os.path.join(os.path.dirname(os.path.abspath(__file__)), 'station_list.json')
        station_list = json.loads(f.read())

    for station in station_list:
        station_code_map[station['name']] = station['code']

    configs.STATION_CODE_MAP = station_code_map  # {}
    del station_list

    logging.config.dictConfig(configs.LOGGING)

    # if platform.system() == "Windows":
    #     settings.CHROME_APP_OPEN_CMD = settings.CHROME_APP_OPEN_CMD_WINDOWS
    # elif platform.system() == 'Linux':
    #     settings.CHROME_APP_OPEN_CMD = settings.CHROME_APP_OPEN_CMD_LINUX
    # elif platform.mac_ver()[0]:
    #     settings.CHROME_APP_OPEN_CMD = settings.CHROME_APP_OPEN_CMD_MacOS
    # else:
    #     settings.CHROME_APP_OPEN_CMD = settings.CHROME_APP_OPEN_CMD_MacOS

    configs.INIT_DONE = True


def run(train_date, train_names, seat_types, from_station, to_station, pay_channel=configs.BANK_ID_WX, passengers=None, **kwargs):
    """
    Booking entry point.
    """
    initialize()
    assert configs.INIT_DONE is True, 'No Initialization'

    date_patten = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    assert date_patten.match(train_date), 'Invalid train_date param. %s' % train_date
    # 验证座位类型集的类型
    assert isinstance(seat_types, (list, tuple)), u'Invalid seat_types param. %s' % seat_types
    # 验证座位类型是否超出范围
    assert frozenset(seat_types) <= frozenset(dict(configs.SEAT_TYPE_CODE_MAP).keys()
                                              ), u'Invalid seat_types param. %s' % seat_types
    # 验证出发地是否在所有集里面
    # print(settings.STATION_CODE_MAP.values())
    assert from_station in configs.STATION_CODE_MAP.values(), 'Invalid from_station param. %s' % from_station
    # 验证目的地是否在所有集里面
    assert to_station in configs.STATION_CODE_MAP.values(), 'Invalid to_station param. %s' % to_station
    # 验证支付方式是否在所有集里面
    assert pay_channel in dict(configs.BANK_ID_MAP).keys(), 'Invalid pay_channel param. %s' % pay_channel

    train_info = {}
    # order_no = None
    check_passengers = False
    passenger_id_nos = []
    booking_status = configs.QUERY_REMAINING_TICKET   # 查询余票
    remaining_ticket_counter = 0  # 计数

    last_auth_time = int(time.time())

    while True:
        try:
            # auth
            if booking_status == configs.QUERY_REMAINING_TICKET and(
                    not configs.COOKIES or not auth_is_login(configs.COOKIES)):
                cookies = auth_qr()
                configs.COOKIES = cookies

            # reauth
            if booking_status != configs.QUERY_REMAINING_TICKET and configs.AUTH_UAMTK and configs.COOKIES:
                if int(time.time()) - last_auth_time >= configs.AUTH_REAUTH_INTERVAL:
                    uamauth_result = auth_reauth(configs.AUTH_UAMTK, configs.COOKIES)
                    configs.COOKIES.update(tk=uamauth_result['apptk'])
                    last_auth_time = int(time.time())
                    _logger.info('%s 重新认证成功' % uamauth_result['username'].encode('utf8'))

            # check passengers
            if booking_status != configs.QUERY_REMAINING_TICKET and not check_passengers:
                passenger_infos = user_passengers()
                if passengers:
                    passenger_name_id_map = {}
                    for passenger_info in passenger_infos:
                        passenger_name_id_map[passenger_info['passenger_name']] = passenger_info['passenger_id_no']

                    assert frozenset(passengers) <= frozenset(passenger_name_id_map.keys()), u'无效的乘客. %s' % json.dumps(
                        list(frozenset(passengers) - frozenset(passenger_name_id_map.keys())), ensure_ascii=False)

                    for passenger in passengers:
                        _logger.info(u'订票乘客信息。姓名：%s 身份证号:%s' % (passenger, passenger_name_id_map[passenger]))
                        passenger_id_nos.append(passenger_name_id_map[passenger])
                else:
                    passenger_id_nos = [passenger_infos[0]['passenger_id_no']]
                    _logger.info(
                        u'订票乘客信息。姓名:%s 身份证号:%s' %
                        (passenger_infos[0]['passenger_name'], passenger_infos[0]['passenger_id_no']))

                check_passengers = True

            # 未完成订单
            if booking_status != configs.QUERY_REMAINING_TICKET and order_check_no_complete():
                booking_status = configs.PAY_ORDER

            _logger.debug('booking status. %s' % dict(configs.BOOKING_STATUS_MAP).get(booking_status, '未知状态'))

            # 查询余票
            if booking_status == configs.QUERY_REMAINING_TICKET:
                remaining_ticket_counter += 1

                _logger.info('查询余票, 已查询%s次!' % remaining_ticket_counter)
                train_info = query_left_tickets(train_date, from_station, to_station, seat_types, train_names)
                print(train_info)
                booking_status = configs.SUBMIT_ORDER   # 提交订单

            # 提交订单
            elif booking_status == configs.SUBMIT_ORDER:
                try:
                    _logger.info('提交订单')
                    order_no = order_submit(passenger_id_nos, **train_info)
                except (exceptions.TrainBaseException, exceptions.BookingBaseException) as e:
                    _logger.info('提交订单失败')
                    booking_status = configs.QUERY_REMAINING_TICKET
                    _logger.exception(e)
                    continue
                else:
                    # submit order successfully
                    if order_no:
                        _logger.info('提交订单成功')
                        booking_status = configs.PAY_ORDER

            # 订单支付
            elif booking_status == configs.PAY_ORDER:
                # 发送信息或邮件
                _logger.info('支付订单')
                # pay_order(pay_channel)
                # pay success and exit
                return
            else:
                assert 'Unkown booking status. %s' % booking_status
        except exceptions.BookingTrainNoLeftTicket as e:
            _logger.info('无票')
            # _logger.exception(e)
            # continue

        except exceptions.TrainUserNotLogin:
            _logger.warn('用户未登录，请重新扫码登录')
            continue

        except exceptions.TrainBaseException as e:
            _logger.error(e)
            _logger.exception(e)

        except Exception as e:
            import traceback
            traceback.print_exc()
            if isinstance(e, AssertionError):
                _logger.exception(e)
                _logger.error('系统内部运行异常，请重新执行程序！')
                os._exit(-1)
            elif isinstance(e, exceptions.BookingOrderCancelExceedLimit):
                _logger.exception(e)
                _logger.error('用户今日订单取消次数超限，请明天再重新抢票！')
                os._exit(-2)
            else:
                print(e)
                _logger.exception(e)

        time.sleep(configs.SLEEP_INTERVAL)


if __name__ == '__main__':
    run('2019-01-28', ['G6317', 'D7521', 'D7529'], ['二等座', '无座'], 'GZQ', 'ZHQ')