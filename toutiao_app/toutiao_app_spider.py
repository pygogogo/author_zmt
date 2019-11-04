#@Time    :2019/10/18 11:32
#@Author  :wuxinghui 
#@FileName: toutiao.py
import sys
import os
curPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import random
import time
import datetime
import re
import pymysql
from redis import Redis
from public.operation_db import select_data,update_data
import logging
from lxml import etree
import threading
import multiprocessing



class touTiaoSpider(threading.Thread):
    formdata = {
        #'keyword': '123',
        'pd': 'user',
        'source': 'search_subtab_switch',
        'traffic_source': '',
        'original_source': '',
        'in_tfs': '',
        'in_ogs': '',
        'format': 'json',
        'count': '10',
        'offset': '0',
        'from': 'media',
        'search_id': '2019101816131001001404902307075AF6'

    }
    headers = [{
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Mobile Safari/537.36'
    },{
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
    },
        {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'
        },
        {'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Mobile Safari/537.36'
        }

    ]

    def __init__(self):
        threading.Thread.__init__(self)
        self.client = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com", port=3306,
                                      password="YZdagKAGawe132sazljjQklf", user="spider", db="spider")
        self.cursor = self.client.cursor()
        self.conn = Redis(host='47.101.128.5', port=6379)
        self.start_time = time.time()
        self.beginTime = time.time()
        self.logger = self.logger_info()
        self.url = 'https://m.toutiao.com/search/'
        self.threadLock = threading.Lock()
        self.queue = multiprocessing.Queue(1000)

    def logger_info(self):
        """日志模块"""
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
        return logger

    def run(self):
        """获取搜索关键字"""
        while True:
            end_time = time.time()
            if end_time - self.start_time > 20*60:
                print('程序休眠中')
                time.sleep(1*60)
                self.start_time = end_time
            self.threadLock.acquire()

            sql = """select words,id from search_words_wxh where toutiao_status=0 and category=2 limit 1  """
            result = select_data(sql)
            if result:
                for i in result :
                    sql="""update search_words_wxh set toutiao_status=1 where id=%s"""% i[1]
                    update_data(sql)
                    self.threadLock.release()
                    self.get_url(i[0])
                    sql = """update search_words_wxh set toutiao_status=2 where id=%s"""% i[1]
                    update_data(sql)
            else:
                print("已经爬取完")
                self.threadLock.release()
                break



    def get_url(self,word):
        """获取详情页的url"""
        print(word)
        self.formdata["keyword"] = word
        #url = 'https://i.snssdk.com/user/profile/homepage/v7/?version_code=719&user_id=1842372960846152&request_source=1&active_tab=dongtai&device_id=123&media_id=1637043622840350'
        for i in range(0,100):
            time.sleep(random.randint(1,3))
            self.formdata["offset"] = str(i*10)
            self.formdata['start_index'] = str(i*10)
            r = 10
            while True:
                if r > 60:
                    break
                try:
                    response = requests.get(self.url, headers=random.choice(self.headers), params=self.formdata,verify=False,timeout=10)
                except requests.exceptions.ReadTimeout:
                    print('请求个人主页超时')
                    time.sleep(r)
                    r += 10
                    continue
                except Exception as result:
                    print('请求2其他错误%s' % result)
                    print("休眠半小时")
                    time.sleep(30*60)
                    continue
                else:
                    break
            search_id = response.headers['X-Tt-Logid']
            self.formdata['search_id'] =search_id
            data = response.json()["dom"]
            if "未找到" not in data:
                if data:
                    print("*"*50)
                    print(response.json())
                    print("*"*50)
                    html = etree.HTML(data)
                    divs = html.xpath("//div[@class='result-content']")
                    for div in divs:

                        url = div.xpath(".//a[contains(@class,'ttfe-flex-item')]/@href")
                        if url:
                            url = url[0]
                        else:
                            continue
                        name_id = re.findall(r"user_id=(\d+)",url)[0]

                        rets = self.conn.sadd('toutiao_author',name_id)
                        if rets == 0:
                            print('重复了:%s'%name_id)
                        else:
                            url = 'https://i.snssdk.com/user/profile/homepage/v7/'+"?"+url.split("?")[1]
                            print(url)
                            self.parse_detail(url)
                else:
                    print("没有数据了")
                    break
            else:
                print("未搜索到")
                break

    def parse_detail(self,url):
        """对详情页进行解析"""
        r = 10
        while True:
            if r > 60:
                break
            try:
                response = requests.get(url,headers=random.choice(self.headers),verify=False,timeout=10)
            except requests.exceptions.ReadTimeout:
                print('请求个人主页超时')
                time.sleep(r)
                r += 10
                continue
            except Exception as result:
                print('请求2其他错误%s' % result)
                print("休眠半小时")
                time.sleep(30 * 60)
                continue
            else:
                break
        data = response.json()["data"]
        autname = data["name"]
        autwebid = data["user_id"]
        autimageurl = data['avatar_url']
        autindex ='https://www.toutiao.com/c/user/%s/'%autwebid
        autfans = data['followers_count']
        autsub = data['description']
        publish_count = data['publish_count']
        if publish_count == 0:
            print("此作者没有文章：%s"%autname)
            return

        try:
            acid = data["user_auth_info"]['auth_type']
        except:
            acid = 0
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

            try:
                sql = '''insert into author_push(apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                self.cursor.execute(sql, (
                    apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask,
                    autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal,
                    autfans))
                self.client.commit()
                print('插入成功')
                self.logger.info("插入数据库成功")
            except Exception as result:
                print('插入失败：%s' % result)
                print("插入作者失败：%s"%autname)
                self.client.rollback()
                self.logger.error("插入数据库失败")




if __name__ == '__main__':
    for i in range(5):
        thread = touTiaoSpider()
        time.sleep(8)
        thread.start()

