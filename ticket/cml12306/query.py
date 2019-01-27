# encoding: utf8
"""
query.py
"""

import re
import os
import copy
import json
import logging

# from hack12306.constants import SEAT_TYPE_CODE_MAP
# from hack12306.query import TrainInfoQueryAPI
# from hack12306.constants import SEAT_TYPE_CODE_MAP
from .base import TrainBaseAPI
from . import configs
from . import exceptions

_logger = logging.getLogger('booking')

__all__ = ('query_left_tickets', 'query_station_code_map',)


class TrainInfoQueryAPI(TrainBaseAPI):
    """
    信息查询
    """

    def info_query_left_tickets(self, train_date, from_station, to_station, purpose_codes='ADULT', **kwargs):
        """
        信息查询-余票查询
        :param train_date 乘车日期
        :param from_station 出发站
        :param to_station 到达站
        :return JSON 数组
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

        url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
        params = [
            ('leftTicketDTO.train_date', train_date),
            ('leftTicketDTO.from_station', from_station),
            ('leftTicketDTO.to_station', to_station),
            ('purpose_codes', purpose_codes),
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' not in resp or 'result' not in resp['data']:
            return []

        trains = []
        for train_s in resp['data']['result']:
            train = train_s.split('|')
            trains.append({
                'secret': train[0],
                'remark': train[1],
                'train_num': train[2],
                'train_name': train[3],
                'from_station': train[4],
                'to_station': train[5],
                'departure_time': train[8],     # 出发时间
                'arrival_time': train[9],       # 到达时间
                'duration': train[10],          # 历时
                configs.SEAT_TYPE_BUSINESS_SEAT: train[32],
                configs.SEAT_TYPE_FIRST_SEAT: train[31],
                configs.SEAT_TYPE_SECONDE_SEAT: train[30],
                # settings.SEAT_TYPE_HIGH_SLEEPER_SEAT: '--',    # TODO 高级软卧
                configs.SEAT_TYPE_SOFT_SLEEPER_SEAT: train[23],
                configs.SEAT_TYPE_HARD_SLEEPER_SEAT: train[28],
                configs.SEAT_TYPE_SOFT_SEAT: train[24],
                configs.SEAT_TYPE_HARD_SEAT: train[29],
                configs.SEAT_TYPE_NO_SEAT: train[26],
            })
        return trains

    def info_query_station_trains(self, train_start_date, train_station_code, **kwargs):
        """
        信息查询-车站(车次)查询
        :param train_start_date 开始日期
        :param train_station_code 车站编码
        :return JSON LIST
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_start_date), 'Invalid train_start_date param. %s' % train_start_date

        url = 'https://kyfw.12306.cn/otn/czxx/query'
        params = {
            'train_start_date': train_start_date,
            'train_station_code': train_station_code
        }
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' in resp and 'data' in resp['data']:
            return resp['data']['data']

    def info_query_train_no(self, train_no, from_station_telecode, to_station_telecode, depart_date, **kwargs):
        """
        信息查询-车次查询
        :param train_no 车次号
        :param from_station_telecode 起始车站编码
        :param to_station_telecode 到站车站编码
        :param depart_date 乘车日期
        :return JSON DICT
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(depart_date), 'Invalid depart_date param. %s' % depart_date

        url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo'
        params = [
            ('train_no', train_no),
            ('from_station_telecode', from_station_telecode),
            ('to_station_telecode', to_station_telecode),
            ('depart_date', depart_date),
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' in resp and 'data' in resp['data']:
            return resp['data']['data']
        else:
            return []

    def info_query_ticket_price(self, train_no, from_station_no, to_station_no, seat_types, train_date, **kwargs):
        """
        信息查询-车票价格
        :param train_no 车次号
        :param from_station_no 始发站
        :param to_station_no 到站
        :param seat_types 席别
        :param train_date 日期
        :return JSON DICT
        """
        date_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

        # TODO 席别枚举检查

        url = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice'
        params = [
            ('train_no', train_no),
            ('from_station_no', from_station_no),
            ('to_station_no', to_station_no),
            ('seat_types', seat_types),
            ('train_date', train_date)
        ]
        resp = self.submit(url, params, method='GET', **kwargs)
        if 'data' in resp:
            return resp['data']
        else:
            return {}

    def info_query_station_list(self, station_version=None, **kwargs):
        """
        信息查询-车站列表
        :param station_version 版本号
        :return JSON 数组
        """
        def _parse_stations(s):
            station_list = []

            s = s.replace(';', '')
            s = s.replace('var station_names =', '')

            s_list = s.split('@')
            s_list.pop(0)

            for station in s_list:
                station_tuple = tuple(station.split('|'))
                station_list.append({
                    'name': station_tuple[1].decode('utf8'),
                    'short_name': station_tuple[0],
                    'code': station_tuple[2],
                    'english_name': station_tuple[3],
                    'index': station_tuple[5]
                })
            return station_list

        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        params = {
            'station_version': station_version or '',
        }
        resp = self.submit(url, params, method='GET', parse_resp=False, **kwargs)
        if not resp.status_code == 200:
            raise exceptions.TrainAPIException(str(resp))

        return _parse_stations(resp.content)

    def info_query_station_list2(self):
        print(os.path.dirname(__file__))
        path = os.path.dirname(__file__)
        with open(os.path.join(path, 'station_list.json'), 'r', encoding='utf-8') as f:
            station_str = f.read()
            station_list = json.loads(station_str)
        return station_list



    def info_query_station_by_name(self, station_name, station_version=None, **kwargs):
        station_list = self.info_query_station_list(station_version)
        for station in station_list:
            if station['name'] == station_name:
                return station
        else:
            return None


def _check_seat_type_is_booking(left_ticket):
    if left_ticket and left_ticket != u'无' and left_ticket != u'*':
        return True
    else:
        return False


def _select_train_and_seat_type(train_names, seat_types, query_trains):
    """
    选择订票车次、席别
    :param train_names 预定的车次列表
    :param seat_types 预定席别列表
    :param query_trains 查询到火车车次列表
    :return select_train, select_seat_type
    """
    def _select_trains(query_trains, train_names=None):
        if train_names:
            select_trains = []
            # 根据订票车次次序，选择车次
            for train_name in train_names:
                for train in query_trains:
                    if train['train_name'] == train_name:
                        select_trains.append(copy.deepcopy(train))
                        break
            return select_trains
        else:
            return query_trains

    def _select_types(trains, seat_types):
        # select_train = None
        # select_seat_type = None

        for train in trains:
            for seat_type in seat_types:
                seat_type_left_ticket = train.get(seat_type, '')
                if _check_seat_type_is_booking(seat_type_left_ticket):
                    select_seat_type = seat_type
                    select_train = copy.deepcopy(train)
                    return select_train, select_seat_type
        else:
            return None, None

    _logger.debug('train_names:%s seat_types:%s' % (json.dumps(train_names, ensure_ascii=False),
                                                    json.dumps(seat_types, ensure_ascii=False)))
    trains = _select_trains(query_trains, train_names)
    # debug trains
    for i in range(min(len(trains), len(train_names or ['']))):
        _logger.debug('query left tickets train info. %s' % json.dumps(trains[i], ensure_ascii=False))

    return _select_types(trains, seat_types)


def query_left_tickets(train_date, from_station, to_station, seat_types, train_names=None):
    """
    信息查询-剩余车票
    :param train_date
    :param from_station
    :param to_station
    :param seat_types
    :param train_names
    :return JSON 对象
    """
    trains = TrainInfoQueryAPI().info_query_left_tickets(train_date, from_station, to_station)
    train_info, select_seat_type = _select_train_and_seat_type(train_names, seat_types, trains)

    if not train_info or not select_seat_type:
        raise exceptions.BookingTrainNoLeftTicket()

    _logger.debug('select train info. %s' % json.dumps(train_info, ensure_ascii=False))

    result = {
        'train_date': train_date,
        'from_station': train_info['from_station'],
        'to_station': train_info['to_station'],
        'seat_type': select_seat_type,
        'seat_type_code': dict(configs.SEAT_TYPE_CODE_MAP)[select_seat_type],
        'departure_time': train_info['departure_time'],
        'arrival_time': train_info['arrival_time'],
        'secret': train_info['secret'],
        'train_name': train_info['train_name'],
        'duration': train_info['duration'],
        'train_num': train_info['train_num']
    }
    return result


def query_station_code_map():
    """
    信息查询-查询车站编码列表
    :return JSON对象
    """
    station_code_map = {}

    stations = TrainInfoQueryAPI().info_query_station_list2()
    for station in stations:
        station_code_map[station['name']] = station['code']

    return station_code_map
