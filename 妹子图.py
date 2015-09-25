import urllib.request
import urllib.error
import os
import sys
import http.client
import time
import re
import random
import math

target = 'http://jandan.net/ooxx/'
proxy_url = 'http://www.xicidaili.com/'
save_path = 'G:\\图片\\妹子图'
max_error_times = 5        #最多允许失败5次，否则放弃该图片下载
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}
enctype = 'utf-8'
proxies = []

def create_localhost():     #生成本地直接访问的proxies
    global proxies
    number = int((math.sqrt(5)-1)/2 * len(proxies))
    for x in range(number):
        proxies.append(None)

def get_result(req_or_url,is_retrieve=False,filename = None):         #取得网页页面
    global max_error_times
    error_time = 0
    while True:
        try:
            if error_time == max_error_times:
                print('失败次数达%d次......放弃操作' % max_error_times)
                return None
            error_time += 1
            if is_retrieve:
                return urllib.request.urlretrieve(req_or_url,filename)
            else:
                return urllib.request.urlopen(req_or_url)
        except urllib.error.URLError as e:
            if hasattr(e,'code'):         
                print(e.code,e.reason)
                change_proxy()
                continue
            elif hasattr(e,'reason'):
                print(e)
                change_proxy()
                continue
        except (ConnectionResetError,http.client.BadStatusLine) as e:
            print(e)
            change_proxy()
            continue
        except TimeoutError as e:
            print(e)
            print('服务器长时间无响应，自动切换代理.....')
            change_proxy()
            continue

def get_proxy():            #从代理页面提取代理IP及端口
    global headers,proxies,proxy_url
    req = urllib.request.Request(proxy_url,None,headers)
    response = get_result(req)
    html = response.read().decode('utf-8')
    p = re.compile(r'''<tr\sclass[^>]*?>\s*?
                                    <td>.+</td>\s*?
                                    <td>(.*)?</td>\s*?
                                    <td>(.*)?</td>\s*?
                                    <td>(.*)?</td>\s*?
                                    <td>(.*)?</td>\s*?
                                    <td>(.*)?</td>\s*?
                                    <td>(.*)?</td>\s*?
                                </tr>''',re.VERBOSE)
    proxy_list = p.findall(html)
    for each_proxy in proxy_list[1:]:
        if each_proxy[4] == 'HTTP':
            proxies.append(each_proxy[0]+':'+each_proxy[1])

def change_proxy():     #切换代理
    proxy = random.choice(proxies)
    if proxy == None:
        proxy_support = urllib.request.ProxyHandler({})
    else:
        proxy_support = urllib.request.ProxyHandler({'http':proxy})
    opener = urllib.request.build_opener(proxy_support)
    opener.addheaders = [('User-Agent',headers['User-Agent'])]
    urllib.request.install_opener(opener)
    print('智能切换代理：%s' % ('本机' if proxy==None else proxy))

def get_page():         #获取最大页数
    global headers,enctype,target
    req = urllib.request.Request(target,None,headers)
    response = get_result(req)
    html = response.read().decode(enctype)
    find_string = 'current-comment-page'
    find_start = html.index(find_string) + len(find_string) + 3
    find_end = html.index(']',find_start+1)
    return int(html[find_start:find_end])

def get_pic(page):      #生成器，返回一个图片链接
    global headers,enctype
    while True:
        url = '%spage-%d' % (target,page)
        print('当前页面：%d' % page)
        req = urllib.request.Request(url,None,headers)
        response = get_result(req)
        if response == None:
            print('获取页面失败.....')
            sys.exit()
        html = response.read().decode(enctype)
        pic = re.compile(r'<img\s+src="(http://(?:ww).+?\.(?:jpg|jpeg|gif))"')
        for pic in pic.finditer(html):
            yield pic.group(1)
        time.sleep(5)
        page -= 1
        if page<1:
            break

def download():     #下载图片
    global headers,save_path
    count = 1
    for pic_url in get_pic(1465):         #get_page()改为页数如1000可从1000页开始下载
        file_name = os.path.split(pic_url)[1]
        if not os.path.isdir(save_path):    #目录不存在就创建
            os.makedirs(save_path)
        get_result(pic_url,True,save_path+'\\'+file_name)
        print('本次成功下载第%d个图片! %s' % (count , pic_url))
        count += 1

if __name__ == '__main__':
    get_proxy() #取得代理
    create_localhost()  #生成本地直接访问proxies
    download()  #开始下载



































