import requests
import re
import time
from subprocess import Popen
from bs4 import BeautifulSoup

try:
    import cookielib
except:
    import http.cookiejar as cookielib
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

s = requests.session()
r = s.get('http://www.zhihu.com', headers=headers)


def getXSRF(r):
    cer = re.compile('name=\"_xsrf\" value=\"(.*)\"', flags=0)
    strlist = cer.findall(r.text)
    return strlist[0]


_xsrf = getXSRF(r)

# print(r.request.headers)
# print(str(int(time.time()*1000)))
Captcha_URL = 'http://www.zhihu.com/captcha.gif?r=' + str(int(time.time() * 1000)) + '&type=login'
r = s.get(Captcha_URL, headers=headers)

with open('code.gif', 'wb') as f:
    f.write(r.content)
Popen('code.gif', shell=True)
captcha = input('captcha: ')
login_data = {
    '_xsrf': _xsrf,
    'phone_num': '电话',
    'password': '密码',
    'remember_me': 'true',
    'captcha': captcha
}

r = s.post('https://www.zhihu.com/login/phone_num', data=login_data, headers=headers)
print(r.text)
url = "https://www.zhihu.com/topic"
r = s.get(url, headers=headers)
# print(r)
data = r.text
# print(data)
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