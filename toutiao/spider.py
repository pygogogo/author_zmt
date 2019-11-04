#coding:gbk
import requests
import random
import time
import datetime
import json
from toutiao.get_UserAgent import main_user_agent
from toutiao.cookie import get_cookie
import re
import pymysql
from redis import Redis
from toutiao.get_fans import get_autfans



class Spider(object):

    url = 'https://www.toutiao.com/api/search/content/'
    formdata = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': '0',
        'format': 'json',
        'keyword': '1',
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '4',
        'from': 'media',
        'pd': 'user',
        #'timestamp': '1568622270068'
    }

    headers = {
        #'cookie': 'csrftoken=185d39889430379d2cc4e60989e44ef5; tt_webid=6731923993248663047; tt_webid=6731923993248663047; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=16cf16b354a378-09846fc3091e0a-5373e62-1fa400-16cf16b354b747; CNZZDATA1259612802=1310668984-1567415102-https%253A%252F%252Fwww.toutiao.com%252F%7C1567415102; _ga=GA1.2.670355303.1567418431; uuid="w:4937269d173d4eb29cfea3d77102a394"; login_flag=86e3d608f997d131a92d67527dc01a8f; sessionid=ce50f76a71fef0715eca023db8dae503; sid_tt=ce50f76a71fef0715eca023db8dae503; odin_tt=0ecf12d82001b4a86dc20f72345e5e7289773ac079d430e8a6c18e2e55edfbb94e480a591bff5f42bdc2dcce8dcd86d192d07bbba98dfaac47a5730b48b842d8; passport_auth_status=c9fb9ffad54dc854a93b293ba8b61b88; sso_auth_status=2d9810ab569f224c1851307833141b33; uid_tt=85bb4dd9245351a16290642aac811f8a; sid_guard="ce50f76a71fef0715eca023db8dae503|1567562356|15552000|Mon\054 02-Mar-2020 01:59:16 GMT"; s_v_web_id=0d1ba59f7a4f6e972049d8a03776de7e; __tasessionId=j7sqlp7of1568100218044',
       #'cookie':'tt_webid=6737408373757265419;WEATHER_CITY=%E5%8C%97%E4%BA%AC;tt_webid=6737408373757265419;csrftoken=94d8beaf366025d22c89e6d485ef6cc2;_s_v_web_id=45867bb633006f7a397ea477a3df5975;_tasessionId=5t7tm3xba1568675137363',
        'cookie':'tt_webid=6737170853257512461; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6737170853257512461; csrftoken=a72571d5fde6cd62195a104abf54c7be; s_v_web_id=dd79c64d899198e747677d4c2f8c3644; __tasessionId=ypogwap011568954630155',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'referer': 'https://www.toutiao.com/search/?keyword=%E9%98%BF',
        'accept-language': 'zh-CN,zh;q=0.9'

    }
    proxy = {'http': '192.168.10.244:8088'}

    def __init__(self):
        self.client = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com", port=3306,
                                 password="YZdagKAGawe132sazljjQklf", user="spider", db="spider")
        self.cursor = self.client.cursor()
        self.conn = Redis(host='127.0.0.1',port=6379)




    def get_page(self):
        with open("words.txt", 'r',encoding='gbk') as fp:
            txt = fp.read()
            txt = re.sub(r'\s|\n|\t', '', txt)
            for word in txt:
                self.formdata['keyword'] = word
                s = 10
                for i in range(0,1000):
                    time.sleep(random.randint(2,5))
                    i = str(i*20)
                    self.formdata['offset'] = i
                    self.headers['User-Agent']=random.choice(main_user_agent)
                    #处理requests异常
                    r = 10
                    while True:
                        if r > 60:
                            break
                        try:
                            response = requests.get(url=self.url,headers=self.headers,params=self.formdata,timeout=20,proxies=self.proxy)
                        except requests.exceptions.ReadTimeout:
                            print('请求个人主页超时')
                            time.sleep(r)
                            r += 10
                            continue
                        except Exception as result:
                            print('请求2其他错误%s' % result)
                            time.sleep(r)
                            r += 10
                            cookie = get_cookie('https://www.toutiao.com/search/?keyword=1')
                            self.headers['cookie'] = cookie
                            continue
                        else:
                            if response.status_code !=200:
                                time.sleep(r)
                                continue
                            else:
                                break
                    print(response.status_code)
                    response = response.json()
                #判断是否返回数据，如果没有，则说明已经没有搜索结果

                    print("try中的响应:%s"%response)
                    datas = response['data']
                    if datas:
                        self.get_info(datas)
                    else:
                        try:
                            token = response['tokens']
                        except Exception as result:
                            print("关于token的错误信息%s"%result)
                            print("cookies失效了")
                            print('存在的cookie%s:'%self.headers['cookie'])
                            cookie = get_cookie('https://www.toutiao.com/search/?keyword=%E4%B8%AD%E5%9B%BD')
                            self.headers['cookie'] = cookie
                            print(s)
                            time.sleep(s)
                            if s > 30:
                                break
                            else:
                                s +=10
                                continue
                        else:
                            print('没有数据了')
                            break



    def get_info(self,datas):
        print("*"*20)
            #提取数据
        for info in datas:
            try:
                acid = info["user_auth_info"]['auth_type']
            except:
                acid = None
            autname = info['name']

            autwebid = info['id']
            autimageurl = info['avatar_url']
            autindex = info['source_url']
            try:
                autfans = info['follow_count']
            except Exception as result:
                print(result)
                autfans = get_autfans(autindex)
            autsub = info['description']
            checktime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            autjointime = checktime
            auttldate = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S')
            checkstate = 1
            isoriginal = None
            auttask = None
            apid = 5
            autsumread = None
            autspiurl = None
            autsumcomment = None
            autdes = None
            autstate = 1
            dic = {'autname': autname, 'autwebid': autwebid, 'autindex': autindex, 'autimageurl': autimageurl,
                   'autfans': autfans, 'apid': apid, 'checktime': checktime, 'acid': acid, 'autspiurl': autspiurl,
                   'autsumcomment': autsumcomment, 'autsumread': autsumread, 'auttask': auttask,
                   'autjointime': autjointime, 'auttldate': auttldate, 'autstate': autstate, 'isoriginal': isoriginal,
                   'checkstate': checkstate, 'autdes': autdes,'autsub':autsub}
            #判断作者名字是否已经存在，存在则pass
            #不存在就存入集合中
            response = self.conn.sadd('toutiao_author',autwebid)
            if response == 0:
                print('重复了')
            else:


                try:
                    sql = '''insert into author(apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                    self.cursor.execute(sql, (
                    apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask,
                    autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal,
                    autfans))
                    self.client.commit()
                    print('插入成功')
                except Exception as result:
                    print('插入失败：%s' % result)
                    self.client.rollback()

if __name__ == '__main__':
    spider = Spider()
    spider.get_page()