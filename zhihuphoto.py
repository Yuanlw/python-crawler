import requests
from bs4 import BeautifulSoup
import os
import json
import re
import time
from subprocess import Popen

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
Captcha_URL = 'http://www.zhihu.com/captcha.gif?r=' + str(int(time.time() * 1000)) + '&type=login'

r = session.get(Captcha_URL, headers=headers)

with open('code.gif', 'wb') as f:
    f.write(r.content)
##打开验证码图片
Popen('code.gif', shell=True)
##等待手工输入
captcha = input('captcha: ')

##登录账号等信息
login_data = {
    '_xsrf': _xsrf,
    'phone_num': '******',
    'password': '*******',
    'remember_me': 'true',
    'captcha': captcha
}


##登录
def _login():
    try:
        r = session.post('https://www.zhihu.com/login/phone_num', data=login_data, headers=headers)
        print(r.text)
    except requests.HTTPError as e:
        if hasattr(e, "reason"):
            print(u"访问失败...")
            return None


def getPageCode(pageUrl):
    try:
        req = session.get(pageUrl, headers=headers)
        print(req.request.headers)
        return req.text
    except requests.HTTPError as e:
        if hasattr(e, 'reason'):
            print(u"打开链接失败..."), e.reason
            return None


def getImageUrl(pageUrl):
    pageCode = getPageCode(pageUrl)
    if not pageCode:
        print("打开网页链接失败..")
        return None
    pattern = re.compile('<a class="author-link".*?<span title=.*?<div class="zh-summary.*?' +
                         '<div class="zm-editable-content.*?>(.*?)</div>', re.S)
    items = re.findall(pattern, pageCode)
    imagesUrl = []
    pattern = re.compile('data-actualsrc="(.*?)">', re.S)
    for item in items:
        urls = re.findall(pattern, item)
        imagesUrl.extend(urls)
    for url in imagesUrl:
        print(url)
    return imagesUrl


def saveImagesFromUrl(pageUrl, filePath):
    imagesUrl = getImageUrl(pageUrl)
    if not imagesUrl:
        print('imagesUrl is empty')
        return
    nameNumber = 0;
    for image in imagesUrl:
        suffixNum = image.rfind('.')
        suffix = image[suffixNum:]
        fileName = filePath + os.sep + str(nameNumber) + suffix
        nameNumber += 1
        print('save in: ', fileName)
        response = requests.get(image)
        contents = response.content
        try:
            with open(fileName, "wb") as pic:
                pic.write(contents)
        except IOError:
            print('Io error')


'''
hello 我是登录
'''
_login()
##问题连接地址
question = "53953519"
question_url = "http://www.zhihu.com/question/" + question
##保存路径
dir = "d:/images/zhihu/miao/test/"
##获取图片并保存
saveImagesFromUrl(question_url, dir)
