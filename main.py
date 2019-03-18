
from ticket.cml12306.run import main00


if __name__ == '__main__':
    main00()


"""
Request URL: https://kyfw.12306.cn/otn/login/userLogin
Request Method: GET
Status Code: 302 Moved Temporarily
Remote Address: 61.145.100.54:443
Referrer Policy: no-referrer-when-downgrade

response:
HTTP/1.1 302 Moved Temporarily
Date: Thu, 14 Feb 2019 02:54:58 GMT
Content-Length: 0
ct: C1_232_68_7
Location: https://kyfw.12306.cn/otn/view/index.html
Content-Language: zh-CN
X-Via: 1.1 PSgdzhdx7za20:30 (Cdn Cache Server V2.0)
Connection: keep-alive
X-Cdn-Src-Port: 12306
Cdn-Src-Ip: 113.119.108.93

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7
Connection: keep-alive
Cookie: 
    JSESSIONID=B4D52DF52974CA0DA7B98950AF4C5508; 
    tk=4uBWilI_2dqbtDR2FlQfiDVZcaiEdHqzIbq_3OlAHWDsvkfRbc2120; 
    _jc_save_wfdc_flag=dc; 
    RAIL_EXPIRATION=1550169907581; 
    RAIL_DEVICEID=TAw6tn8Ty6Id10tL3b_J0MbBqnhnO_TcZIQ0cKUVO5jxpeD8129E8_EACn90diU8kafGMDB5fB5ftj1sd6P-jEeNG0y1tO1OEqyVjBajOziKTrw_vyF0FlKJOfg7u9WbAiYO61PAtyFNTTEqoPIGZSYxIOn2CqWs; 
    _jc_save_fromStation=%u840D%u4E61%u5317%2CPBG; 
    route=6f50b51faa11b987e576cdb301e545c4; 
    BIGipServerotn=1156055306.50210.0000; 
    BIGipServerportal=3067347210.17183.0000; 
    BIGipServerpassport=854065418.50215.0000; 
    _jc_save_toStation=%u5E7F%u5DDE%2CGZQ; 
    _jc_save_fromDate=2019-02-14; 
    _jc_save_toDate=2019-02-14
Host: kyfw.12306.cn
Referer: https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36
"""