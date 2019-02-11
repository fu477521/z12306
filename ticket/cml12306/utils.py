# encoding: utf8
"""
utils.py
@author
@description Util functions
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""

import six
import uuid
import json
import urllib
import decimal
import datetime

import os
import json
import platform
import requests
from PIL import Image

def cookie_str_to_dict(cookie_str):
    cookies = []
    for cookie in [cookie.strip() for cookie in cookie_str.split(';')]:
        cookies.append(cookie.split('='))
    return dict(cookies)


def get_cookie_from_str(cookie_str):
    cookie_dict = cookie_str_to_dict(cookie_str)
    return {
        'BIGipServerotn': cookie_dict.get('BIGipServerotn', ''),
        'JSESSIONID': cookie_dict.get('JSESSIONID', ''),
        'tk': cookie_dict.get('tk', ''),
        'route': cookie_dict.get('route', ''),
    }


def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def today():
    return datetime.date.today()


def urlencode(params):
    assert isinstance(params, (list, dict))

    if isinstance(params, list):
        param_list = []
        for param in params:
            # param_list.append(urllib.urlencode({param[0]: param[1]}))   # Python2
            # print(param[0], param[1])
            print(param)
            param_list.append(urllib.parse.urlencode({param[0]: param[1]}))
        return '&'.join(param_list)
    elif isinstance(params, dict):
        return urllib.parse.urlencode(params)
    else:
        assert False, 'Unsupported type params'


def time_cst_format(time):
    """
    格式化为 CST 格式时间
    """
    CST_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)'
    assert isinstance(time, datetime.datetime), 'Invalid time param. %s' % time
    return time.strftime(CST_FORMAT)


class JSONEncoder(json.JSONEncoder):

    """
    JSONEncoder subclass that knows how to encode date/time/timedelta,
    decimal types, generators and other basic python objects.
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'
            return representation
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            representation = obj.isoformat()
            return representation
        elif isinstance(obj, datetime.timedelta):
            return six.text_type(obj.total_seconds())
        elif isinstance(obj, decimal.Decimal):
            # Serializers will coerce decimals to strings by default.
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return six.text_type(obj)
        elif isinstance(obj, bytes):
            # Best-effort for binary blobs. See #4187.
            return obj.decode('utf-8')
        elif hasattr(obj, 'tolist'):
            # Numpy arrays and array scalars.
            return obj.tolist()
        elif hasattr(obj, '__getitem__'):
            try:
                return dict(obj)
            except Exception:
                pass
        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)
        return super(JSONEncoder, self).default(obj)


def gen_passenger_ticket_tuple(seat_type, passenger_flag, passenger_type,
                               name, id_type, id_no, mobile, **kwargs):
    l = [seat_type, passenger_flag, passenger_type, name, id_type, id_no, mobile, 'N']
    # return tuple([i.encode('utf8') for i in l])
    return tuple(l)


def gen_old_passenge_tuple(name, id_type, id_no, passenger_type, **kwargs):
    l = [name, id_type, id_no,  str(passenger_type)+'_']
    # return tuple([i.encode('utf8') for i in l])
    return tuple(l)


def qr_terminal_draw(filepath):
    assert isinstance(filepath, (str))

    if not os.path.exists(filepath):
        raise Exception('file not exists. %s' % filepath)

    if platform.system() == "Windows":
        white_block = '▇'
        black_block = '  '
        new_line = '\n'
    else:
        white_block = '\033[1;37;47m  '
        black_block = '\033[1;37;40m  '
        new_line = '\033[0m\n'

    output = ''
    im = Image.open(filepath)
    im = im.resize((21, 21))

    pixels = im.load()

    output += white_block * (im.width + 2) + new_line
    for h in range(im.height):
        output += white_block
        for w in range(im.width):
            pixel = pixels[w,h]     # NOQA
            if pixel[0] == 0:
                output += black_block
            elif pixel[0] == 255:
                output += white_block
            else:
                assert 'Unsupported pixel. %s' % pixel

        else:
            output += white_block + new_line
    output += white_block * (im.width + 2) + new_line

    return output


def get_public_ip():
    resp = requests.get('http://httpbin.org/ip')
    if resp.status_code != 200:
        raise Exception('Network error')
    return json.loads(resp.content)['origin'].encode('utf8')


def check_seat_types(seat_types):
    from .configs import SEAT_TYPE_CODE_MAP

    assert isinstance(seat_types, (list, tuple))
    if not frozenset(seat_types) <= frozenset(dict(SEAT_TYPE_CODE_MAP).keys()):
        return False
    return True


