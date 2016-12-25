import requests
import re
import time
from subprocess import Popen
from bs4 import BeautifulSoup

# try:
#     import cookielib
# except:
#     import http.cookiejar as cookielib

##headers
headers = {
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.zhihu.com',
    'Accept-Language': 'zh-CN',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0(Windows NT 6.1;WOW64;Trident/7.0;rv:11.0)like Gecko',
    'Host': 'www.zhihu.com'
}

##session
session = requests.session()
##获取知乎登录页
request = session.get('http://www.zhihu.com', headers=headers)


##获取页面唯一标示码 _xsrf 方法
def getXSRF(request):
    cer = re.compile('name=\"_xsrf\" value=\"(.*)\"', flags=0)
    strlist = cer.findall(request.text)
    return strlist[0]


##获取_xsrf 值
_xsrf = getXSRF(request)


# print(r.request.headers)
# print(str(int(time.time()*1000)))
##获取验证码图片
def getCaptcha():
    try:
        Captcha_URL = 'http://www.zhihu.com/captcha.gif?r=' + str(int(time.time() * 1000)) + '&type=login'
        r = session.get(Captcha_URL, headers=headers)
        with open('code.gif', 'wb') as f:
            f.write(r.content)
    except requests.HTTPError as e:
        if hasattr(e, "reason"):
            print("登陆失败..."), e.reason
            return None


##打开验证码图片
Popen('code.gif', shell=True)
##等待手工输入
captcha = input('captcha: ')

##登录账号等信息
login_data = {
    '_xsrf': _xsrf,
    'phone_num': '****',
    'password': '*****',
    'remember_me': 'true',
    'captcha': captcha
}


##登录
def login():
    try:
        r = session.post('https://www.zhihu.com/login/phone_num', data=login_data, headers=headers)
        print(r.text)
    except requests.HTTPError as e:
        if hasattr(e, "reason"):
            print("登陆失败..."), e.reason
            return None


##要抓取的页面
def getTopic(url):
    try:
        # url = "https://www.zhihu.com/topic"
        r = session.get(url, headers=headers)
        # print(r)
        data = r.text
        return data
    except requests.HTTPError as e:
        if hasattr(e, "reason"):
            print("登陆失败..."), e.reason
            return None


##解析页面元素
def praseData(url):
    data = getTopic(url)
    bs = BeautifulSoup(data, "html.parser")
    questions = bs.find_all('a', {"class": "question_link"})
    # print(questions)
    for question in questions:
        print(question.get_text() + 'https://www.zhihu.com' + question['href'])


        #     print(question.get_text())
        #     print(question.getText.text)
        #     print(question.getText)
        # answers=bs.find_all('div',{"class":"zh-summary summary clearfix"})
        # for answer in answers:
        #     print(answer.get_text())


login()
url = "https://www.zhihu.com/topic"
praseData(url)
