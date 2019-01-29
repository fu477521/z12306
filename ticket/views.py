import re
import json
import base64
import datetime
from django.shortcuts import render, HttpResponse, HttpResponseRedirect   #, reverse
from django.urls import reverse
from django.contrib import messages
from .cml12306.query import query_station_code_map
from .cml12306.run import run
from .cml12306.auth import get_qr, check_qr

def Index(request):

    return render(request, 'index12306.html')

def Ticket(request):
    from_station = request.POST.get('from_station', '')
    to_station = request.POST.get('to_station', '')
    date = request.POST.get('date', '')
    print(type(date))
    train_str = request.POST.get('train_num', '')
    seat_types = request.POST.getlist('seats', '')
    passengers = request.POST.get('passengers', '')
    train_num = train_str.split(' ')
    print(from_station, to_station, date, train_num, seat_types, passengers)
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
            train_names=train_num,
            pay_channel='微信',
            date=date,
            seat_types=seat_types,
            passengers=passengers,
        )

        img, uuid, cookie_dict = get_qr()
        # print('img:', img)

        data_str = str(data)
        cookie_str = str(cookie_dict)
        # data_value = str(base64.b64encode(data_str.encode('utf-8')), 'utf-8')
        # cookie_value = str(base64.b64encode(cookie_str.encode('utf-8')), 'utf-8')
        data_value = json.dumps(data)
        cookie_value = json.dumps(cookie_dict)
        print('data:', data_value)
        print('cookie_dict:', type(cookie_value), cookie_value)
        context = {'img': img, 'uuid': uuid, 'data': data}
        response = render(request, 'login12306.html', context)
        response.set_cookie('uuid', uuid)
        response.set_cookie('data', data_value)
        response.set_cookie('cookie_dict', cookie_value)
        return response
        # return HttpResponseRedirect(reverse('ticket:Login', args=(data,)))
    else:
        return HttpResponse("input data is error!!")

def Check_login(request):
    uuid = request.COOKIES.get('uuid')
    cookie_str = request.COOKIES.get('cookie_dict')
    data_str = request.COOKIES.get('data')
    cookie_dict = json.loads(cookie_str)
    # result = check_qr(uuid, cookie_dict)
    result = 2
    if result == 1:
        response = HttpResponseRedirect(reverse('ticket:login'))
        response.set_cookie('uuid', uuid)
        return response
        # return HttpResponseRedirect(reverse('ticket:login', args=(data,)))
    else:
        # return HttpResponse("扫码失败，重新刷新！")
        response = HttpResponseRedirect(reverse('ticket:login'))
        response.set_cookie('uuid', uuid)
        response.set_cookie('data', data_str)
        response.set_cookie('cookie_dict', cookie_str)
        return response

def Login(request):
    # return HttpResponse('It is ok!!!')
    data = json.loads(request.COOKIES.get('data', {}))
    uuid = request.COOKIES.get('uuid', '')
    cookie_dict = json.loads(request.COOKIES.get('cookie_dict', ''))
    print('Logindata:', type(data), data)
    print('Loginuuid:', type(uuid), uuid)
    print('Logincook:', type(cookie_dict), cookie_dict)
    date = data.get('date', '')
    train_names = data.get('train_names', '')
    seat_types = data.get('seat_types', '')
    from_station = data.get('from_station', '')
    to_station = data.get('to_station', '')
    pay_channel = data.get('pay_channel', '')
    passengers = data.get('passengers', '')
    print(date, train_names, seat_types, from_station, to_station, pay_channel, passengers)
    print(type(date), type(train_names), type(seat_types), type(from_station), type(to_station), type(pay_channel), type(passengers))
    # run(date, train_names, seat_types, from_station, to_station, pay_channel, passengers=passengers)
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
