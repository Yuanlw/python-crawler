# -*- coding: utf-8 -*-
from queue import Queue

import Login
import requests
import re, os,time
from subprocess import Popen
from threading import Thread
# import Queuelib
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
    'phone_num': '*******',
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






queue = Queue(50)
filePath = "D:/images/zhihu/miao/test/meinv"
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
                'params': '{"url_token":' + str(21436118) + ',"pagesize": "10",' + \
                          '"offset":' + str(size) + "}",
                '_xsrf': _xsrf,

            }
            size += 10
            page = session.post(url, headers=headers, data=postdata)
            print("翻页：",page.text)
            ret = eval(page.text)
            print("eval是处理了什么：",ret)
            listMsg = ret['msg']
            print("listMsg又是什么鬼：",listMsg)
            if not listMsg:
                print("图片URL获取完毕, 页数: ", (size - 10) / 10)
                queue.join()
                isRun = False
                break
            pattern = re.compile('data-actualsrc="(.*?)">', re.S)
            global queue
            for pageUrl in listMsg:
                items = re.findall(pattern, pageUrl)
                for item in items:  # 这里去掉得到的图片URL中的转义字符'\\'
                    imageUrl = item.replace("\\", "")
                    queue.put(imageUrl)


class DownloadImgAndWriteToFile(Thread):
    def run(self):
        nameNumber = 0
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
                response = session.get(image, timeout=20)
                contents = response.content
                with open(fileName, "wb") as pic:
                    pic.write(contents)
                    print("+++++++++++++保存图片："+str(nameNumber)+" 张")
            except requests.exceptions.ConnectionError:
                print('连接超时,URL: ', image)
            except IOError:
                print('Io error')
        print('图片下载完毕')


if __name__ == '__main__':
    _login()
    start = time.clock()
    urlThread = GetImageURLThread()
    downloadThread = DownloadImgAndWriteToFile()
    urlThread.start()
    downloadThread.start()

    urlThread.join()
    downloadThread.join()
    end = time.clock()

# print("耗时：%.03f 秒" %(end - start))
    print("耗时：%.03f 秒" %(end - start))