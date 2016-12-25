# -*- coding: utf-8 -*-
from queue import Queue

import Login
import requests
import re, os,time
from subprocess import Popen
from threading import Thread
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
# import Queue
# from Queue
"""
知乎翻页获取图片,使用两个线程,一个生产者，一个消费者
"""

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

# ##登录
# Login.login()

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






queue = Queue(50)
filePath = "D:/images/zhihu/miao/"
global isRun
isRun = True


class GetImageURLThread(Thread):
    def run(self):
        url = "https://www.zhihu.com/node/QuestionAnswerListV2"
        method = 'next'
        size = 10

        if not os.path.exists(filePath):
            os.makedirs(filePath)

            # 循环翻页直到结束
        while (True):
            print('===========offset: ', size)
            postdata = {
                'method': 'next',
                'params': '{"url_token":' + str(36435092) + ',"pagesize": "10",' + \
                          '"offset":' + str(size) + "}",
                '_xsrf': _xsrf,

            }
            size += 10
            page = session.post(url, headers=headers, data=postdata)
            ret = eval(page.text) ##转义
            listMsg = ret['msg'] ##获取msg,到数组中
            if not listMsg:
                print("图片URL获取完毕, 页数: ", (size - 10) / 10)
                queue.join()
                isRun = False
                print("是否已无数据：",isRun)
                break


            pattern = re.compile('data-actualsrc="(.*?)">', re.S)
            global queue
            for pageUrl in listMsg:
                # bs = BeautifulSoup(pageUrl, "html.parser")
                items = re.findall(pattern, pageUrl)
                # items = bs.find_all('data-actualsrc',pageUrl)
                for item in items:  # 这里去掉得到的图片URL中的转义字符'\\'
                    imageUrl = item.replace("\\", "")
                    queue.put(imageUrl)


class DownloadImgAndWriteToFile(Thread):
    def run(self):
        nameNumber = 1000
        global queue
        while isRun:
            image = queue.get()
            queue.task_done()
            suffixNum = image.rfind('.')
            suffix = image[suffixNum:]
            fileName = filePath + os.sep + str(nameNumber) + suffix
            nameNumber += 1
            try:
                # 设置超时重试次数及超时时间单位秒
                session.mount(image, HTTPAdapter(max_retries=3))
                response = session.get(image, timeout=2)
                contents = response.content
                with open(fileName, "wb") as pic:
                    pic.write(contents)
                    print("+++++++++++++保存图片："+str(nameNumber)+" 张")
                    print("怎们还不结束：",isRun)
            except requests.exceptions.ConnectionError:
                print('连接超时,URL: ', image)
            except IOError:
                print('Io error')
        print('图片下载完毕')


if __name__ == '__main__':
    _login()
    ##第一页
    ##问题连接地址
    question = "36435092"
    question_url = "http://www.zhihu.com/question/" + question
    saveImagesFromUrl(question_url,filePath)
    #翻页
    start = time.clock()
    urlThread = GetImageURLThread()
    downloadThread = DownloadImgAndWriteToFile()
    urlThread.start()
    downloadThread.start()

    urlThread.join()
    downloadThread.join()
    end = time.clock()

# print("耗时：%.03f 秒" %(end - start))
#     print("耗时：%.03f 秒" %(end - start))