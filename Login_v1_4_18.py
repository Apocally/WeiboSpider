#-*- coding: utf-8 -*-
import urllib
import urllib.request
import http.cookiejar
from urllib.parse import quote
import base64
import rsa
import binascii
import re


class WeiboLogin(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.login_url = r'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        self.prelogin_url = r'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)&_=1483076313825'
        self.headers ={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'
        }
        self.cookie_filename = r'cookie.txt'
    def login(self):
        pubkey, servertime, nonce, rsakv = Prelogin(self.prelogin_url)
        post_data = PostData(self.username,self.password,pubkey,servertime,nonce, rsakv)

        # 步骤一：创建opener
        cj = http.cookiejar.LWPCookieJar(self.cookie_filename)  # 指定Cookie容器
        handler = urllib.request.HTTPCookieProcessor(cj)  # 创建handler
        opener = urllib.request.build_opener(handler)  # 创建opener

        # 步骤二：创建请求
        req = urllib.request.Request(self.login_url, headers=self.headers)

        # 步骤三：请求网址
        response = opener.open(req,data=post_data)
        response_text = response.read().decode('GBK')

        # 提取重定向网址
        try:
            pa = re.compile(r'location\.replace\(\'(.*?)\'\)')
            redirect_url = pa.search(response_text).group(1)
            print('------------REDIRECT------------')
            print('Redirect to: ', redirect_url)
            login_req = urllib.request.Request(redirect_url,headers=self.headers)
            login_response = opener.open(login_req)  # 登录，获取登录cookie
            login_response_text = login_response.read().decode('utf-8')
            uniqueid_pa = re.compile(r'\"uniqueid\":\"(.*?)\"')
            uniqueid = uniqueid_pa.search(login_response_text).group(1)
            web_weibo_url = "http://weibo.com/u/%s/home?wvr=5&uut=fin&from=reg" % uniqueid
            homepage_req = urllib.request.Request(web_weibo_url,headers=self.headers)
            homepage_response = opener.open(homepage_req)  # 登录主页
            cj.save()
            print('Login Success!')
            return homepage_response
        except:
            print('Login Error!')
            return None


# 请求prelogin.php，获得pubkey, servertime, nonce, retcode, rsakv

def Prelogin(prelogin_url):
    data = urllib.request.urlopen(prelogin_url).read().decode('utf-8')
    p = re.compile('\((.*)\)')  # 匹配括号内的内容
    data_str = p.search(data).group(1)  # 返回最后一组符合条件的字符串
    server_data_dict = eval(data_str)  #字符串转换成字典
    print('------------SERVER DATA:------------')
    print_list = ['pubkey', 'servertime', 'nonce']
    for each_item in print_list:
        print(str(each_item) + '=' + str(server_data_dict[each_item]))
    pubkey = server_data_dict['pubkey']
    servertime = server_data_dict['servertime']
    nonce = server_data_dict['nonce']
    rsakv = server_data_dict['rsakv']
    return pubkey, servertime, nonce, rsakv


def PostData(username,password,pubkey,servertime,nonce, rsakv):
    su, sp = RSAEncoder(username,password,pubkey,servertime,nonce)
    post_para = {
        'encoding':'UTF-8',
        'entry':'weibo',
        'from':'',
        'gateway':'1',
        'nonce':nonce,
        'pagerefer':'',
        'prelt':'645',
        'pwencode':'rsa2',
        'returntype':'META',
        'rsakv':rsakv,
        'savestate':'7',
        'servertime':str(servertime),
        'service':'miniblog',
        'sp':sp,
        'sr':'1920*1080',
        'su':su,
        'url':r'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'useticket':'1',
        'vsnf':'1',
    }

    print('------------POST DATA:------------')
    print_list = ['su', 'sp', 'servertime', 'nonce']
    for each_item in print_list:
        print(each_item + '=' + str(post_para[each_item]))
    post_data = urllib.parse.urlencode(post_para).encode('utf-8')
    return post_data


def RSAEncoder(username, password, pubkey, servertime, nonce):
    # 处理用户名
    su_url = urllib.parse.quote_plus(username)  # 转换成url格式， 将‘@’转换成‘%40’
    su_encoded = su_url.encode('utf-8')  # 转换成字节串，以满足base64编码输入需求
    su = base64.b64encode(su_encoded)  # base64加密，处理用户名
    su = su.decode('utf-8')

    #处理密码
    rsaPublickey = int(pubkey, 16)
    e = int('10001', 16)
    key = rsa.PublicKey(rsaPublickey, e)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
    passwd = rsa.encrypt(message.encode('utf-8'),key)
    sp = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return su, sp


def LoginMain():
    username = input('User Name: ')
    password = input('Password: ')
    try:
        loginer = WeiboLogin(username, password)
        response = loginer.login()
        # print(response.read().decode('utf-8'))    # 打印主页
        return response
    except:
        return None

if __name__ == '__main__':
	LoginMain()
