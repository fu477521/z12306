# encoding: utf8
"""
order.py
@author
@description Order
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""

import re
import time
import json
import urllib
import datetime
import logging

from . import configs
from . import exceptions
from .base import TrainBaseAPI
from .auth import check_login
# from .query import TrainInfoQueryAPI
from .user import TrainUserAPI
# from .utils import time_cst_format, tomorrow
from .utils import (tomorrow, JSONEncoder, time_cst_format,
                             gen_old_passenge_tuple, gen_passenger_ticket_tuple)



_logger = logging.getLogger('booking')

__all__ = ('TrainOrderAPI', 'order_check_no_complete', 'order_submit', 'order_no_complete')


class TrainOrderAPI(TrainBaseAPI):
    """
    订单
    """

    @check_login
    def order_submit_order(self, secret_str, train_date, query_from_station_name=None, query_to_station_name=None,
                           purpose_codes='ADULT', tour_flag='dc', back_train_date=None, undefined=None,
                           **kwargs):
        """
        订单-下单-提交订单
        :param secret_str
        :param train_date 乘车日期
        :param back_train_date 返程日期
        :param tour_flag
        :param purpose_codes 默认为“ADULT”
        :param query_from_station_name 查询车站名称
        :param query_to_station_name 查询到站名称
        :return Boolean True-成功  False-失败
        """
        date_pattern = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

        if back_train_date:
            assert date_pattern.match(back_train_date), 'Invalid back_train_date param. %s' % back_train_date
        else:
            back_train_date = tomorrow().strftime('%Y-%m-%d')

        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        params = {
            'secretStr': urllib.parse.unquote(secret_str),
            'train_date': train_date,
            'back_train_date': back_train_date,
            'tour_flag': tour_flag,
            'purpose_codes': purpose_codes,
            'query_from_station_name': query_from_station_name or '',
            'query_to_station_name': query_to_station_name or '',
            'undefined': undefined or ''
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        if resp['httpstatus'] == 200 and resp['status'] is True:
            return True
        else:
            raise exceptions.TrainAPIException('submit order error. %s' % json.dumps(resp, ensure_ascii=False))

    @check_login
    def order_confirm_passenger(self, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客初始化
        :param _json_att
        :return JSON 对象
        """
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        params = {
            '_json_att': _json_att or ''
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        token_pattern = re.compile(r"var globalRepeatSubmitToken = '(\S+)'")
        token = token_pattern.search(resp.text).group(1)

        ticket_info_pattern = re.compile(r'var ticketInfoForPassengerForm=(\{.+\})?')
        ticket_info = json.loads(ticket_info_pattern.search(resp.text).group(1).replace("'", '"'))

        order_request_params_pattern = re.compile(r'var orderRequestDTO=(\{.+\})?')
        order_request_params = json.loads(order_request_params_pattern.search(resp.text).group(1).replace("'", '"'))

        resp = {
            'token': token,
            'ticket_info': ticket_info,
            'order_request_params': order_request_params,
        }
        return resp

    @check_login
    def order_confirm_passenger_check_order(self, token, passenger_ticket_str, old_passenger_str, tour_flag='dc',
                                            cancel_flag=2, bed_level_order_num='000000000000000000000000000000',
                                            whatsSelect=1, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，检查订单
        :param cancel_flag
        :param bed_level_order_num
        :param passenger_ticket_str
        :param old_passenger_str
        :param tour_flag
        :param whatsSelect
        :param _json_att
        :param token
        :return JSON 对象
        """

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        params = {
            'cancel_flag': cancel_flag,
            'bed_level_order_num': bed_level_order_num,
            'passengerTicketStr': passenger_ticket_str,
            'oldPassengerStr': old_passenger_str,
            'tour_flag': tour_flag,
            'randCode': '',
            'whatsSelect': whatsSelect,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token
        }

        resp = self.submit(url, params, method='POST', **kwargs)
        return resp['data']

    @check_login
    def order_confirm_passenger_get_queue_count(self, train_date, train_no, seat_type,
                                                from_station_telecode, to_station_telecode, left_ticket,
                                                token, station_train_code, purpose_codes, train_location,
                                                _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，获取排队数量
        :param train_date CST格式时间
        :param train_no
        :param seat_type 席别
        :param from_station_telecode 出发站编码
        :param to_station_telecode 到站编码
        :param left_ticket
        :param token
        :param station_train_code
        :param purpose_codes
        :param train_location
        :param _json_att
        :return JSON 对象
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date
        train_date = time_cst_format(datetime.datetime.strptime(train_date, '%Y-%m-%d'))

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        params = {
            'train_date': train_date,
            'train_no': train_no,
            'stationTrainCode': station_train_code,
            'seatType': seat_type,
            'fromStationTelecode': from_station_telecode,
            'toStationTelecode': to_station_telecode,
            'leftTicket': left_ticket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        return resp['data']

    @check_login
    def order_confirm_passenger_confirm_single_for_queue(self, passenger_ticket_str, old_passenger_str, purpose_codes,
                                                         key_check_isChange, left_ticket, train_location,
                                                         token, whats_select='1', dw_all='N', room_type=None,
                                                         seat_detail_type=None, choose_seats=None, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，确认车票
        :param passenger_ticket
        :param old_passenger
        :param purpose_codes
        :param key_check_isChange
        :param left_ticket
        :param train_location
        :param choose_seats
        :param seat_detail_type
        :param whats_select
        :param root_type
        :param dw_all
        :param _json_att
        :param token
        :return JSON对象
        """
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        params = {
            'passengerTicketStr': passenger_ticket_str,
            'oldPassengerStr':  old_passenger_str,
            'randCode': '',
            'purpose_codes': purpose_codes,
            'key_check_isChange': key_check_isChange,
            'leftTicketStr': left_ticket,
            'train_location': train_location,
            'choose_seats': choose_seats or '',
            'seatDetailType': seat_detail_type,
            'whatsSelect': whats_select,
            'roomType': room_type,
            'dwAll': dw_all,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        return resp['data']

    @check_login
    def order_confirm_passenger_query_order(self, token, tour_flag='dc', random=None, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，查询
        :param random
        :pram tour_flag
        :pram token
        :pram _json_att
        """
        random = random or str(int(time.time()*100))

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
        params = [
            ('random', random),
            ('tourFlag', tour_flag),
            ('_json_att', _json_att or ''),
            ('REPEAT_SUBMIT_TOKEN', token),
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        return resp['data']

    @check_login
    def order_confirm_passenger_result_order(self, sequence_no, token, _json_att=None, **kwargs):
        """
        订单-下单-确认乘客，订单结果
        :pram senquence_no
        :param _json_att
        :param token
        """
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        params = {
            'orderSequence_no': sequence_no,
            '_json_att': _json_att or '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        resp = self.submit(url, params, method="POST", **kwargs)
        return resp['data']

    @check_login
    def order_query(self, start_date, end_date, type='1', sequeue_train_name='',
                    come_from_flag='my_order', query_where='G', **kwargs):
        """
        订单-查询
        :param start_date 开始日期，格式YYYY-mm-dd
        :param end_date 结束日期，格式 YYYY-mm-dd
        :param type 查询类型 "1"-按订票日期查询，"2"-按乘车日期查询
        :param sequeue_train_name 订单号，车次，姓名
        :param come_from_flag 来源标志 “my_order”-全部，“my_resign”-可改签，“my_cs_resgin”-可变更到站，“my_refund”-可退款
        :param query_where 订单来源 "G"-未出行，"H"-历史订单
        :return JSON LIST
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

        assert date_pattern.match(start_date), 'invalid start_date params. %s' % start_date
        assert date_pattern.match(end_date), 'invalid end_date params. %s' % end_date
        assert type in dict(configs.ORDER_QUERY_TYPE), 'invalid type params. %s' % type
        assert come_from_flag in dict(
            configs.ORDER_COME_FROM_FLAG), 'invalid come_from_flag params. %s' % come_from_flag
        assert query_where in dict(configs.ORDER_WHERE), 'invalid query_where params. %s' % query_where

        url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrder'
        params = {
            'come_from_flag': come_from_flag,
            'query_where': query_where,
            'queryStartDate': start_date,
            'queryEndDate': end_date,
            'queryType': type,
            'sequence_train_name': sequeue_train_name or '',
            'pageIndex': kwargs.get('page_offset', 0),
            'pageSize': kwargs.get('page_size', 8),
        }
        resp = self.submit(url, params, method='POST', **kwargs)
        if 'data' in resp and 'OrderDTODataList' in resp['data']:
            return resp['data']['OrderDTODataList']
        else:
            return []

    @check_login
    def order_query_no_complete(self, **kwargs):
        """
        订单-未完成订单
        """
        url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'
        resp = self.submit(url, method='POST', **kwargs)
        if 'data' in resp and 'orderDBList' in resp['data']:
            return resp['data']['orderDBList']
        else:
            return []


def order_no_complete(cookies=configs.COOKIES):
    """
    订单-未支付订单
    """
    orders = TrainOrderAPI().order_query_no_complete(cookies=cookies)
    _logger.debug('order no complete orders. %s' % json.dumps(orders, ensure_ascii=False))
    if not orders:
        return None
    return orders[0]['sequence_no']


def order_check_no_complete(cookies):
    """
    订单-检查是有未支付订单
    :return True:有支付订单 False:没有未支付订单
    """
    if order_no_complete(cookies):
        return True
    else:
        return False

import copy

def order_submit(passenger_id_nos, cookies, **train_info):
    """
    订单-提交订单
    :param passenger_id_nos 乘客身份证列表
    :param **train_info 乘车信息
    :return order_no 订单号
    """

    assert isinstance(
        passenger_id_nos, (list, tuple)), 'Invalid passenger_id_nos param. %s' % json.dumps(
        passenger_id_nos, ensure_ascii=False)
    assert passenger_id_nos, 'Invalid passenger_id_nos param. %s' % json.dumps(passenger_id_nos, ensure_ascii=False)

    train_order_api = TrainOrderAPI()

    # 1. 下单-提交订单
    submit_order_result = train_order_api.order_submit_order(
        train_info['secret'],
        train_info['train_date'],
        cookies=cookies)
    _logger.debug('order submit order result. %s' % submit_order_result)

    # 2. 下单-确认乘客
    confirm_passenger_result = train_order_api.order_confirm_passenger(cookies=cookies)
    _logger.debug('order confirm passenger result. %s' % json.dumps(
        confirm_passenger_result, ensure_ascii=False, cls=JSONEncoder))

    # 3. 下单-检查订单信息
    passengers = TrainUserAPI().user_passengers(cookies=cookies)

    select_passengers = []
    for passenger in passengers:
        if passenger['passenger_id_no'] in passenger_id_nos:
            select_passengers.append(copy.deepcopy(passenger))

    assert select_passengers, '乘客不存在. %s' % json.dumps(passenger_id_nos, ensure_ascii=False)
    print("====>下单-检查订单信息:", select_passengers)
    passenger_ticket_list = []
    old_passenger_list = []
    for passenger_info in select_passengers:
        passenger_ticket_list.append(gen_passenger_ticket_tuple(
            train_info['seat_type_code'],
            passenger_info['passenger_flag'],
            passenger_info['passenger_type'],
            passenger_info['passenger_name'],
            passenger_info['passenger_id_type_code'],
            passenger_info['passenger_id_no'],
            passenger_info['mobile_no']))
        old_passenger_list.append(
            gen_old_passenge_tuple(
                passenger_info['passenger_name'],
                passenger_info['passenger_id_type_code'],
                passenger_info['passenger_id_no'],
                passenger_info['passenger_type']))
    print('order====>', passenger_ticket_list)
    passenger_ticket_str = '_'.join([','.join(p) for p in passenger_ticket_list])
    print('order====>', passenger_ticket_str)
    old_passenger_str = ''.join([','.join(p) for p in old_passenger_list])
    print('order====>', old_passenger_str)
    check_order_result = train_order_api.order_confirm_passenger_check_order(
        confirm_passenger_result['token'],
        passenger_ticket_str, old_passenger_str, cookies=cookies)
    _logger.debug('order check order result. %s' % json.dumps(check_order_result, ensure_ascii=False, cls=JSONEncoder))
    if not check_order_result['submitStatus']:
        raise exceptions.BookingSubmitOrderError(check_order_result.get('errMsg', u'提交订单失败').encode('utf8'))

    # 4. 下单-获取排队数量
    queue_count_result = train_order_api.order_confirm_passenger_get_queue_count(
        train_info['train_date'],
        train_info['train_num'],
        train_info['seat_type_code'],
        train_info['from_station'],
        train_info['to_station'],
        confirm_passenger_result['ticket_info']['leftTicketStr'],
        confirm_passenger_result['token'],
        confirm_passenger_result['order_request_params']['station_train_code'],
        confirm_passenger_result['ticket_info']['queryLeftTicketRequestDTO']['purpose_codes'],
        confirm_passenger_result['ticket_info']['train_location'],
        cookies=cookies,
    )
    _logger.info('order confirm passenger get queue count result. %s' % json.dumps(
        queue_count_result, ensure_ascii=False, cls=JSONEncoder))

    # 5. 下单-确认车票
    confirm_ticket_result = train_order_api.order_confirm_passenger_confirm_single_for_queue(
        passenger_ticket_str, old_passenger_str,
        confirm_passenger_result['ticket_info']['queryLeftTicketRequestDTO']['purpose_codes'],
        confirm_passenger_result['ticket_info']['key_check_isChange'],
        confirm_passenger_result['ticket_info']['leftTicketStr'],
        confirm_passenger_result['ticket_info']['train_location'],
        confirm_passenger_result['token'], cookies=cookies)
    _logger.info('order confirm passenger confirm ticket result. %s' % json.dumps(
        confirm_ticket_result, ensure_ascii=False, cls=JSONEncoder))

    # 6. 下单-查询订单
    try_times = 4
    while try_times > 0:
        query_order_result = train_order_api.order_confirm_passenger_query_order(
            confirm_passenger_result['token'], cookies=cookies)
        _logger.debug('order confirm passenger query order result. %s' % json.dumps(
            query_order_result, ensure_ascii=False, cls=JSONEncoder))

        if query_order_result['orderId']:
            # order submit successfully
            break
        else:
            # 今日订单取消次数超限，无法继续订票
            error_code = query_order_result.get('errorcode')
            error_msg = query_order_result.get('msg', '').encode('utf8')
            order_cancel_exceed_limit_pattern = re.compile(r'取消次数过多')

            if error_code == '0' and order_cancel_exceed_limit_pattern.search(error_msg):
               raise exceptions.BookingOrderCancelExceedLimit(query_order_result['msg'].encode('utf8'))

        time.sleep(0.5)
        try_times -= 1
    else:
        raise exceptions.BookingOrderQueryTimeOut()


    # 7. 下单-订单结果查询
    order_result = train_order_api.order_confirm_passenger_result_order(
        query_order_result['orderId'], confirm_passenger_result['token'], cookies=cookies)
    _logger.debug('order result. %s' % json.dumps(order_result, ensure_ascii=False))

    _logger.info(
        '恭喜你！抢票成功。订单号：%s 车次：%s 座位席别：%s 乘车日期：%s 出发站：%s 到达站：%s 历时:%s' %
        (query_order_result['orderId'],
         train_info['train_name'],
         train_info['seat_type'],
         train_info['train_date'],
         train_info['from_station'],
         train_info['to_station'],
         train_info['duration']))

    return query_order_result['orderId']