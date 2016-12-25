import requests
import re
# import Popen
headers = {
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.findicons.com',
    'Accept-Language': 'zh-CN',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0(Windows NT 6.1;WOW64;Trident/7.0;rv:11.0)like Gecko',
    'Host': 'www.findicons.com'
}


url = "http://findicons.com/pack/2787/beautiful_flat_icons"
data = requests.get(url,timeout=600)

k = re.split(r'\s+',data.text)
s = []
sp = []
si = []
for i in k :
    if (re.match(r'src',i) or re.match(r'href',i)):
        if (not re.match(r'href="#"',i)):
            if (re.match(r'.*?png"',i) or re.match(r'.*?ico"',i)):
                if (re.match(r'src',i)):
                    s.append(i)

for it in s :
    if (re.match(r'.*?png"',it)):
        sp.append(it)

cnt = 0
cou = 1
for it in sp:
    m = re.search(r'src="(.*?)"',it)
    iturl = m.group(1)
    print(iturl)
    if (iturl[0]=='/'):
        continue;
    web = requests.get(iturl,timeout=600)
    itdata = web.content
    if (cnt%3==1 and cnt>=4 and cou<=30):
        f = open('d:/images/'+str(cou)+'.png',"wb")
        cou = cou+1
        f.write(itdata)
        f.close()
        print(it)
    cnt = cnt+1


