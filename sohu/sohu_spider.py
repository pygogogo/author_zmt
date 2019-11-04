#coding:utf-8
import sys
import os
curPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import random
import time
import datetime
import time
from lxml import etree
import re
import pymysql
from redis import Redis
from public.operation_db import select_data,update_data
import threading
import logging


class Spider(threading.Thread):
        url ='https://search.sohu.com/search/meta'
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://m.sohu.com',
            'Referer': 'https://m.sohu.com/search?spm=smwp.home.hdn.2.1567735197591T6Ww2MV&keyword=%E5%8D%B0%E5%BA%A6%E5%A4%A7%E5%9D%9D%E5%9D%8D%E5%A1%8C',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Connection': 'close'
        }
        formdata = {
            'keyword': '好',
            'terminalType': 'wap',
            'from': '20',
            'SUV': '190902122840TNX3',
            'source': 'wap-sohu',
            'briefHL': '1',
            'spm-pre': 'smwp.home.hdn.2.1568078364173v20RPmV',
            'spm': 'smwp.srpage.0.0.1568078373931kJKH1ke',
            'size': '20',
            'searchType': 'media',
            'subSeaType': '0',
            'queryType': 'history',
            'queryId': '15680783771735Lit276',
            'pvId': '1568078373931kJKH1ke',
            'refer': 'https://m.sohu.com/?pvid=000115_3w_index&jump=front'
        }

        proxy = {'http':'192.168.10.244:8088'}
        main_user_agent = [
            'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.33 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
            'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE']



        def __init__(self):
            threading.Thread.__init__(self)
            self.client = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com", port=3306,
                                     password="YZdagKAGawe132sazljjQklf", user="spider", db="spider")
            self.cursor = self.client.cursor()
            self.conn = Redis(host='47.101.128.5',port=6379)
            self.start_time = time.time()
            self.threadLock = threading.Lock()
            self.logger = self.logger_info()

        def logger_info(self):
            logger = logging.getLogger('author_push')
            logger.setLevel(logging.DEBUG)
            fh = logging.FileHandler('sohu.log')
            fh.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            logger.addHandler(fh)
            logger.addHandler(ch)
            return logger

        def run(self):
            while True:
                end_time = time.time()
                if end_time - self.start_time > 15 * 60:
                    print('程序休眠中')
                    time.sleep(60)
                    self.start_time = end_time
                sql = """select words,id from search_words_wxh where sohu_status=0 limit 1"""
                result = select_data(sql)
                if result:
                    for i in result:
                        sql = """update search_words_wxh set sohu_status=1 where id=%s""" % i[1]
                        update_data(sql)
                        self.get_page(i[0])
                        sql = """update search_words_wxh set sohu_status=2 where id=%s""" % i[1]
                        update_data(sql)
                else:
                    print("已经爬取完")
                    print("休眠20分钟")
                    time.sleep(20*60)
                    continue

        def get_page(self,word):
            print("*"*50)
            print(word)
            print("*"*50)
            self.formdata['keyword'] = word
            #对于返回的结果进行分页获取
            for i in range(0,1000):
                time.sleep(1)
                i = str(i*20)
                self.formdata['from'] = i
                self.headers['User-Agent']=random.choice(self.main_user_agent)
                #response = requests.get(url=self.url,headers=self.headers,params=self.formdata,timeout=20,proxies=random.choice(self.proxy))
                r = 10
                while True:
                    if r > 60:
                        break
                    try:
                        response = requests.get(url=self.url,headers=self.headers,params=self.formdata,timeout=20)
                        print(response.status_code)
                    except requests.exceptions.ReadTimeout:
                        print('请求个人主页超时')
                        self.logger.error("请求个人主页超时")
                        time.sleep(r)
                        r += 10
                        continue
                    except Exception as result:
                        print('请求2其他错误%s' % result)
                        self.logger.error('请求2其他错误%s' % result)
                        time.sleep(r)
                        r += 10
                        continue
                    else:
                        if response.status_code != 200:
                            time.sleep(r)
                            r += 10
                            continue
                        else:
                            break
                print(response.status_code)
                response = response.json()
            #判断是否返回数据，如果没有，则说明已经没有搜索结果
                try:
                    datas = response['data']['media']
                    print("&"*20)
                    print(datas)
                    print("&" * 20)
                    self.get_info(datas)
                except Exception as result:
                    print(result)
                    break


        def get_info(self,datas):
            print("*"*20)
            for data in datas:
                # 作者名称
                autname = data['userName']
                # 文章数
                newscount = data['scoreMap']['newsCount']
                if newscount == 0:
                    print('此作者没有文章:%s'%autname)
                    continue
                # 作者分类编号
                acid = int(data['mediaType'])
                # 作者主页
                autindex = data['weiboUrl']
                # 作者头像
                autimageurl = data['avatorUrl']
                # 作者简介
                autsub = data['description']
                # 阅读量
                autsumread = int(data['scoreMap']['totalPv'])
                # 作者平台编号
                print(autindex)
                autwebid= re.findall(r'.*?xpt=(.*)',autindex,re.DOTALL)[0]
                print("*"*20)
                print(autwebid)
                print("*" * 20)
                checktime = datetime.datetime.now().strftime('%Y-%m-%d-%T')
                apid = 8
                autspiurl = None
                autsumcomment = 0
                autfans = 0
                auttask = 1
                auttldate = datetime.datetime.now().strftime('%Y-%m-%d-%T')
                autjointime = checktime
                autstate = 1
                autdes = autsub
                isoriginal = None
                checkstate = 1
                #判断作者名字是否已经存在，存在则pass
                #不存在就存入集合中
                response = self.conn.sadd('sohu_author',autwebid)
                if response == 0:
                    print('重复了')
                else:
                    try:
                        sql = '''insert into author_push(apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                        self.cursor.execute(sql, (
                            apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate,
                            auttask,
                            autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment,
                            isoriginal,
                            autfans))
                        self.client.commit()
                        print('插入成功')
                        self.logger.info("插入数据库成功")
                    except Exception as result:
                        print('插入失败：%s'%result)
                        self.client.rollback()
                        self.logger.error("插入数据库失败")


if __name__ == '__main__':
    for i in range(1):
        thread = Spider()
        thread.start()
        time.sleep(2)