import re
import datetime
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from .cml12306.query import query_station_code_map
from .cml12306.run import run
from .cml12306.auth import get_qr

def Index(request):

    return render(request, 'index12306.html')

def Ticket(request):
    from_station = request.POST.get('from_station', '')
    to_station = request.POST.get('to_station', '')
    date = request.POST.get('date', '')
    print(type(date))
    train_num = request.POST.get('train_num', '')
    seat_types = request.POST.getlist('seats', '')
    passengers = request.POST.get('passengers', '')

    print(from_station, to_station, date, train_num, seat_types)
    station_code_map = query_station_code_map()
    try:
        ########################################################################
        messages.error(request, '未找到出发车站.') if not from_station in station_code_map.keys() else print('日期有效！')
        messages.error(request, '未找到目的车站.') if not to_station in station_code_map.keys() else print('日期有效！')
        ########################################################################
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        messages.error(request, '乘车日期无效.') if not date_pattern.match(date) else 'haha'
        ########################################################################
        try:
            today = datetime.date.today()
            train_date_time = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            messages.error(request, '乘车日期必须大于今天.') if not train_date_time >= today else print('日期有效！')
        except ValueError as e:   # time data '2019-0128' does not match format '%Y-%m-%d'
            messages.add_message(request, messages.ERROR, '日期格式不对！')
            print(e)
    except Exception as ee:
        import traceback
        traceback.print_exc(ee)
    result = messages.get_messages(request)
    for res in result:
        print("===>", res)
    if not result:
        data = dict(
            from_station=station_code_map[from_station],
            to_station=station_code_map[to_station],
            train_names=train_num.split(' '),
            pay_channel='微信',
            date=date,
            seat_types=seat_types,
            passengers=passengers,
        )

        img = get_qr()
        context = {'img': img, 'data': data}
        #
        return render(request, 'login12306.html', context)
        # return HttpResponseRedirect(reverse('ticket:Login', args=(data,)))
    else:
        return HttpResponse("input data is error!!")

def Login(request, data):
    for _ in range(30):  # 15秒内扫码登录
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
    run(date, train_names, seat_types, from_station, to_station, pay_channel, passengers=passengers)
    return HttpResponse('It is ok!!!')

def Send_messsage(request):
    pass
    # full_message = name + email + subject + message
    # print(full_message)
    # print(type(subject))
    # print(type(message))
    # print(type(from_email))
    # if subject and message:
    #     try:
    #         send_mail(subject, full_message, from_email, ['caimengli@selmuch.com'])
    #     except BadHeaderError:
    #         return HttpResponse('Invalid header found.')
    #     # return HttpResponseRedirect('/contact/thanks/')
    #     return HttpResponse('Thank you for your suggestion')
    # else:
    #     # In reality we'd use a form class
    #     # to get proper validation errors.
    #     return HttpResponse('Make sure all fields are entered and valid.')
