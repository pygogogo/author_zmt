#coding:gbk
import sys
import os
curPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import random
import time
import datetime
import json
from spider_moudel.toutiao1.get_UserAgent import main_user_agent
from spider_moudel.toutiao1.cookie import get_cookie
import re
import pymysql
from redis import Redis
from spider_moudel.toutiao1.get_fans import get_autfans
from spider_moudel.toutiao1.key_words import *
from public.operation_db import select_data,update_data
from spider_moudel.toutiao1.toutiao_account import account_hearder_id

import logging
logger = logging.getLogger('author_push')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('toutiao.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)




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

    }




    def __init__(self):
        self.client = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com", port=3306,
                                 password="YZdagKAGawe132sazljjQklf", user="spider", db="spider")
        self.cursor = self.client.cursor()
        self.conn = Redis(host='47.101.128.5',port=6379)
        self.start_time = time.time()
        self.account_id, self.headers = account_hearder_id()
        self.beginTime = time.time()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'referer': 'https://www.toutiao.com/search/?keyword=123',
            'cookie':'tt_webid=6748940126652679692; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6748940126652679692; csrftoken=7c30902f82c69e91d338f0fa46c43f07; __tasessionId=g2m9fre5g1571445405725; s_v_web_id=1d259fd8006a11386d465d734728cd1e'
        }
    def get_words(self):
        while True:
            end_time = time.time()
            if end_time - self.start_time > 30 * 60:
                print('程序休眠中')
                self.account_id, self.headers = account_hearder_id()
                time.sleep(5*60)
                self.start_time = end_time


            # finalTime = time.time()
            # if finalTime-self.beginTime >60*60:
            #
            #     print('更换cookie')
            #     cookie = get_cookie('https://www.toutiao.com')
            #     print("*" * 50)
            #     print(cookie)
            #     print("*" * 50)
            #     self.headers['cookie'] = cookie
            #     self.beginTime = finalTime
            sql = """select words,id from search_words_wxh where toutiao_status=0 and category=2  order by id  desc limit 1"""
            result = select_data(sql)
            if result:
                for i in result :
                    sql="""update search_words_wxh set toutiao_status=1 where id=%s"""% i[1]
                    update_data(sql)
                    self.get_page(i[0])
                    sql = """update search_words_wxh set toutiao_status=2 where id=%s"""% i[1]
                    update_data(sql)
            else:
                print("已经爬取完")
                break

    def get_page(self,word):
        print("*"*50)
        print(word)
        print("*" * 50)
        self.formdata['keyword'] = word
        s = 10
        for i in range(0,1000):
            time.sleep(random.randint(5,10))
            i = str(i*20)
            self.formdata['offset'] = i
            self.headers['User-Agent']=random.choice(main_user_agent)
            #处理requests异常
            r = 10
            while True:
                if r > 60:
                    break
                try:
                    print(self.headers)
                    print(self.formdata)
                    response = requests.get(url=self.url,headers=self.headers,params=self.formdata,timeout=20,)
                except requests.exceptions.ReadTimeout:
                    print('请求个人主页超时')
                    time.sleep(r)
                    r += 10
                    continue
                except Exception as result:
                    print('请求2其他错误%s' % result)
                    time.sleep(15*60)
                    # r += 10
                    # cookie = get_cookie('https://www.toutiao.com')
                    # print("*"*50)
                    # print(cookie)
                    # print("*"*50)
                    # self.headers['cookie'] = cookie
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
                    logger.error("关于token的错误信息%s|||cookies失效了"%result)
                    time.sleep(15*60)
                    #print('存在的cookie%s:'%self.headers['cookie'])
                    # self.headers['cookie'] = get_cookie('https://www.toutiao.com')
                    return
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
                acid = 0
            autname = info['name']
            # 通过是否有media_id来判断作者是否有作品
            if 'media_id' not in info :
                print("此作者没有文章:%s"%autname)
                continue
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
            auttldate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            checkstate = 1
            isoriginal = None
            auttask = 1
            apid = 5
            autsumread = 0
            autspiurl = None
            autsumcomment = 0
            autdes = autsub
            autstate = 1
            response = self.conn.sadd('toutiao_author',autwebid)
            if response == 0:
                print('重复了')
            else:
                try:
                    sql = '''insert into author_push(apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                    self.cursor.execute(sql, (
                    apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask,
                    autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal,
                    autfans))
                    self.client.commit()
                    print('插入成功')
                    logger.info("插入数据库成功")
                except Exception as result:
                    print('插入失败：%s' % result)
                    self.client.rollback()
                    logger.error("插入数据库失败")


if __name__ == '__main__':
    spider = Spider()
    spider.get_words()