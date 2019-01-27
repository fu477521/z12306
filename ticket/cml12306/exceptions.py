# encoding: utf8
"""
exceptions.py
"""

class TrainBaseException(Exception):
    """
    12306异常
    """


class TrainRequestException(TrainBaseException):
    """
    12306请求异常
    """


class TrainAPIException(TrainBaseException):
    """
    12306 API 异常
    """

class TrainUserNotLogin(TrainAPIException):
    """
    用户未登录
    """

class BookingBaseException(Exception):
    """
    订票异常
    """


class BookingOrderNoExists(BookingBaseException):
    """
    订单不存在
    """


class BookingTrainNoLeftTicket(BookingBaseException):
    """
    无票
    """
    def __str__(self):
        return repr('无票')


class BookingOrderQueryTimeOut(BookingBaseException):
    """
    订单查询超时
    """


class BookingOrderCancelExceedLimit(BookingBaseException):
    """
    订单取消次数超限
    """

class BookingSubmitOrderError(BookingBaseException):
    """
    提交订单是吧
    """