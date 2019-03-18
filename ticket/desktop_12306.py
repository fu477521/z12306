# -*- coding:utf-8 -*-

from splinter.browser import Browser
from time import sleep
import traceback
import time,sys

class huoche(object):
    driver_name = ''
    executable_path = ''
    username = u"28593@qq.com"
    passwd = u"f4"

    starts = u"陆丰,LLQ"
    ends = u"广州,GZQ"
    dtime = u"2018-02-24"
    #车次
    order = 0
    #乘客名
    users = [u"立",u"明"]
    #席位
    xb = u"二等座"
    pz = u"成人票"

    ticket_url = "https://kyfw.12306.cn/otn/login/leftTicket/init"
    login_url = "https://kyfw.12306.cn/otn/login/init"
    initmy_url = "https://kyfw.12306.cn/otn/index/initMy12306"
    buy_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

    def __init__(self):
        self.driver_name="firefox"
        self.executable_path="C:\Python27\Lib\site-packages\splinter\driver\webdriver"

    def login(self):
        self.driver.visit(self.login_url)
        self.driver.fill("loginUserDTO.user_name",self.username)
        #sleep(1)
        self.driver.fill("userDTO.password",self.passwd)
        print(u"请输入验证码。。。")
        while True:
            if self.driver.url != self.initmy_url:
                sleep(1)
            else:
                break
    def start(self):
        self.driver = Browser() #driver_name = self.driver_name,executable_path = self.executable_path)
        self.driver.driver.set_window_size(1400,1000)
        self.login()
        #sleep(1)
        self.driver.visit(self.ticket_url)
        try:
            print(u"购票页面开始.....")
            #sleep(1)
            #加载查询信息
            self.driver.cookies.add({"_jc_save_fromStation":self.starts})
            self.driver.cookies.add({"_jc_save_toStation":self.ends})
            self.driver.cookies.add({"_jc_save_fromDate":self.dtime})

            self.driver.reload()

            count = 0
            if self.order != 0:
                while self.driver.url == self.ticket_url:
                    self.driver.find_by_id("a_search_ticket").click()
                    count += 1
                    print(u"循环点击%s" % count)
                    try:
                        self.driver.find_by_text(u"预订")[self.order - 1].click()
                    except Exception as e:
                        print(e)
                        print(u"还没开始预订")
                        continue
            else:
                while self.driver.url == self.ticket_url:
                    self.driver.find_by_id("a_search_ticket").click()
                    count += 1
                    print(u"else 循环点击%s"% count)
                    try:
                        for i in self.driver.find_by_text(u"预订"):
                            i.click()
                            sleep(1)
                    except Exception as e:
                        print(e)
                        print(u"else还没开始预订")
                        continue
            print(u"开始预订")
            sleep(1)
            print(u"开始选择用户")
            for user in self.users:
                self.driver.find_by_text(user).last.click()

            print(u"提交订单")
            sleep(0.5)
            self.driver.find_by_id('submitOrder_id').click()
            sleep(0.5)
            self.driver.find_by_id('qr_submit_id').click()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    huoche = huoche()
    huoche.start()