# encoding: utf8
"""
auth.py
@author
@description Authentication
@created Mon Jan 07 2019 13:17:16 GMT+0800 (CST)
"""
import os
import re
import time
import json
import base64
import logging

# from PIL import Image

from .base import TrainBaseAPI
from . import exceptions
from . import configs

_logger = logging.getLogger('booking')

__all__ = ('TrainAuthAPI', 'check_login', 'auth_qr', 'auth_reauth', 'auth_is_login')



def check_login(f):
    """
    用户登录检查装饰器
    """
    def wrapper(*args, **kwargs):
        assert isinstance(args[0], TrainBaseAPI), 'decorated function must be TrainBaseAPI method'
        cookies = kwargs.get('cookies', None)
        if not cookies:
            raise exceptions.TrainUserNotLogin()
        if not TrainAuthAPI().auth_check_login(**kwargs):
            raise exceptions.TrainUserNotLogin()
        return f(*args, **kwargs)
    return wrapper

class TrainAuthAPI(TrainBaseAPI):
    """
    认证
    """
    def auth_check_login(self, cookies=None, **kwargs):
        """
        用户-检查是否登录
        :params cookies: 用户 Session 信息
        :return True:已登录 False:未登录
        """
        if not cookies:
            return False

        assert isinstance(cookies, dict)

        url = 'https://kyfw.12306.cn/otn/login/conf'
        resp = self.submit(url, method='POST', cookies=cookies)
        if resp['data']['is_login'] == 'Y':
            return True
        else:
            return False

    def auth_init(self, **kwargs):
        """
        认证-初始化，获取 cookies 信息
        :return JSON DICT
        """
        route_pattern = re.compile(r'route=[0-9, a-z]*;')
        jsessionid_pattern = re.compile(r'JSESSIONID=[0-9, a-z, A-Z]*;')
        bigipserverotn_pattern = re.compile(r'BIGipServerotn=[0-9, \.]*;')

        url = 'https://kyfw.12306.cn/otn/login/conf'
        resp = self.submit(url, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        cookie_str = resp.headers['Set-Cookie']
        cookie_dict = {
            'route': route_pattern.search(cookie_str).group().split('=')[1].strip(';'),
            'JSESSIONID': jsessionid_pattern.search(cookie_str).group().split('=')[1].strip(';'),
            'BIGipServerotn': bigipserverotn_pattern.search(cookie_str).group().split('=')[1].strip(';'),
        }
        return cookie_dict

    def auth_qr_get(self, **kwargs):
        """
        认证-获取登录二维码
        :return JSON对象  {"result_message":"生成二维码成功",
                          "result_code":"0",
                          "image":"xxx"}
        """
        url = 'https://kyfw.12306.cn/passport/web/create-qr64'
        params = {
            'appid': 'otn'
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        print('++++>', type(resp.text))  # str: {'result_code': -4, 'result_message': '系统维护时间'}
        if resp.status_code != 200:
            raise exceptions.TrainRequestException(str(resp))
        if json.loads(resp.text)['result_code'] == -4:
            raise exceptions.TrainRequestException('系统维护时间')
        return json.loads(resp.text)

    def auth_qr_check(self, uuid, **kwargs):
        """
        认证-检查二维码是否登录
        :param uuid 获取二维码请求中返回的 UUID
        :return COOKIES JSON 对象 {"result_message":"二维码状态查询成功","result_code":"0"}
        """
        assert isinstance(uuid, (str,))

        url = 'https://kyfw.12306.cn/passport/web/checkqr'
        params = {
            'uuid': uuid,
            'appid': 'otn',
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        return json.loads(resp.content)

    def auth_uamtk(self, uamtk, **kwargs):
        """
        认证-UAM流票
        :param uamtk 流票
        :return JSON 对象
        """
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        params = {
            'uamtk': uamtk,
            'appid': 'otn',
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()

        return json.loads(resp.content)

    def auth_uamauth(self, apptk, **kwargs):
        """
        认证-UAM认证
        :param apptk
        :return TODO
        """
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        params = {
            'tk': apptk
        }
        resp = self.submit(url, params, method='POST', parse_resp=False, **kwargs)
        if resp.status_code != 200:
            raise exceptions.TrainRequestException()
        return json.loads(resp.content)



def _uamtk_set(uamtk):
    configs.AUTH_UAMTK = uamtk


def _uamtk_get():
    return configs.AUTH_UAMTK


def auth_is_login(cookies=None):
    """
    检查用户是否登录
    :param cookies JSON对象
    :return True已登录, False未登录
    """
    result = TrainAuthAPI().auth_check_login(cookies=cookies)
    if not result:
        _logger.debug('会话已过期，请重新登录!')
    return result


def auth_reauth(uamtk, cookie_dict):
    """
    重新认证
    :param aumtk
    :param cookie_dict
    :return JSON对象
    """
    assert uamtk is not None
    assert isinstance(cookie_dict, dict)

    train_auth_api = TrainAuthAPI()

    uamtk_result = train_auth_api.auth_uamtk(uamtk, cookies=cookie_dict)
    _logger.debug('4. auth uamtk result. %s' % json.dumps(uamtk_result, ensure_ascii=False))

    uamauth_result = train_auth_api.auth_uamauth(uamtk_result['newapptk'], cookies=cookie_dict)
    _logger.debug('5. auth uamauth result. %s' % json.dumps(uamauth_result, ensure_ascii=False))

    return uamauth_result


def auth_qr():
    """
    认证-二维码登录
    """
    filepath = ''
    try:
        # qr_img_path = '/tmp/12306/booking/login-qr-%s.jpeg' % uuid.uuid1().hex
        qr_img_path = os.path.join(os.path.abspath(os.path.curdir), 'qr_img')

        train_auth_api = TrainAuthAPI()

        _logger.debug('1. auth init')
        cookie_dict = train_auth_api.auth_init()

        _logger.debug('2. auth get qr')
        result = train_auth_api.auth_qr_get(cookies=cookie_dict)
        assert isinstance(result, dict)
        qr_uuid = result['uuid']

        if not os.path.exists(qr_img_path):
            os.makedirs(qr_img_path)


        filepath = os.path.join(qr_img_path, 'login-qr-%s.jpeg' % qr_uuid)
        with open(filepath, 'wb') as f:
            img = base64.b64decode(result['image'])
            print(type(img))
            # print(img)
            f.write(base64.b64decode(result['image']))

        # 用浏览器打开二维码图片
        # filepath = os.path.join(qr_img_path, 'login-qr-%s.jpeg' % uuid.uuid1().hex)
        # filepath = os.path.join(qr_img_path, 'login-qr-%s.jpeg' % qr_uuid)
        cmd = configs.CHROME_APP_OPEN_CMD.format(filepath=filepath)
        os.system(cmd)

        _logger.debug('3. auth check qr')
        for _ in range(30):    # 15秒内扫码登录
            _logger.info('请扫描二维码登录！')
            qr_check_result = train_auth_api.auth_qr_check(qr_uuid, cookies=cookie_dict)
            _logger.debug('check qr result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
            if qr_check_result['result_code'] == "2":
                _logger.debug('qr check success result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
                _logger.info('二维码扫描成功！')
                break
            time.sleep(1)
        else:
            _logger.error('二维码扫描失败，重新生成二维码')
            raise exceptions.TrainUserNotLogin('扫描述二维码失败')

        _uamtk_set(qr_check_result['uamtk'])
        uamauth_result = auth_reauth(_uamtk_get(), cookie_dict)
        _logger.info('%s 登录成功。' % uamauth_result['username'].encode('utf8'))

        cookies = {
            'tk': uamauth_result['apptk']
        }
        cookies.update(**cookie_dict)
        _logger.debug('cookies. %s' % json.dumps(cookies, ensure_ascii=False,))

        # user_info_result = TrainUserAPI().user_info(cookies=cookies)
        # _logger.debug('%s login successfully.' % user_info_result['name'])

        return cookies
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)



def get_qr():
    train_auth_api = TrainAuthAPI()
    cookie_dict = train_auth_api.auth_init()
    result = train_auth_api.auth_qr_get(cookies=cookie_dict)
    assert isinstance(result, dict)
    qr_uuid = result['uuid']
    # img = base64.b64decode(result['image'])
    img = result['image']
    return img, qr_uuid, cookie_dict

def check_qr(qr_uuid, cookie_dict):
    train_auth_api = TrainAuthAPI()
    for _ in range(15):  # 15秒内扫码登录
        _logger.info('check_qr请扫描二维码登录！')
        qr_check_result = train_auth_api.auth_qr_check(qr_uuid, cookies=cookie_dict)
        _logger.debug('check qr result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
        if qr_check_result['result_code'] == "2":
            _logger.debug('qr check success result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
            _logger.info('check_qr二维码扫描成功！')
            break
        time.sleep(1)
    else:
        _logger.error('二维码扫描失败，重新生成二维码')
        return None, None

    _uamtk = qr_check_result['uamtk']
    uamtk_result = train_auth_api.auth_uamtk(_uamtk, cookies=cookie_dict)
    uamauth_result = train_auth_api.auth_uamauth(uamtk_result['newapptk'], cookies=cookie_dict)
    cookies = {
        'tk': uamauth_result['apptk']
    }
    cookies.update(**cookie_dict)
    return cookies, _uamtk
