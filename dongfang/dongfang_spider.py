#@Time    :2019/10/24 14:02
#@Author  :wuxinghui 
#@FileName: dongfang_auto.py
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import datetime
import time
from redis import Redis
import pymysql
from lxml import etree
from public.operation_db import select_data,update_data
import logging
import threading


class spider(threading.Thread):
    data = {
        'accid': '849823746',
        'start': '',
        'size': '20',
        'ime': '867649033725736',
        'position': '湖南',
        'softtype': 'TouTiao',
        'softname': 'DFTTAndroid',
        'appqid': 'vivo190906',
        'apptypeid': 'DFTT',
        'ver': '2.5.6',
        'os': 'Android8.1.0',
        'appver': '020506',
        'deviceid': '36526ee30b9fe25d'
    }
    art_data  ={
        'appqid': 'vivo190906',
        'apptypeid': 'DFTT',
        'appver': '020506',
        'authorid': '200000000000470',
        'authorname': '一诺老师',
        'deviceid': '36526ee30b9fe25d',
        'ime': '867649033725736',
        'newsnum': '20',
        'os': 'Android8.1.0',
        'position': '湖南',
        'softname': 'DFTTAndroid',
        'softtype': 'TouTiao',
        'startcol': '',
        'ttaccid': '849823746',
        'type': 'article',
        'ver': '2.5.6',
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '375',
        'Host': 'dfh.dftoutiao.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.4.1'
    }
    def __init__(self):
        threading.Thread.__init__(self)
        self.url = 'https://dfh.dftoutiao.com/dfh_dingyue/gzip/searchdfh'
        self.key = 'f3cccfe506dbbb36'
        self.client = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com", port=3306,password="YZdagKAGawe132sazljjQklf", user="spider", db="spider")
        self.cursor = self.client.cursor()
        self.conn = Redis(host='47.101.128.5', port=6379)
        self.start_time = time.time()
        self.key_url  = "http://192.168.34.153:8082/getappkey?category=df1"
        self.data['key'] = self.key
        self.art_url = "https://dfh.dftoutiao.com/dfh_news/gzip/getnews"
        self.art_data['key'] = self.key
        self.logger = self.logger_info()
        self.threadLock = threading.Lock()
    def __del__(self):
        self.client.close()

    def get_key(self):
        response = requests.get(self.key_url)
        print(response.json())
        self.key = response.json()['appkey']
    def logger_info(self):
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
        while True:
            end_time = time.time()
            if end_time - self.start_time > 20 * 60:
                print('程序休眠中')
                time.sleep(1*60)
                self.start_time = end_time
            self.threadLock.acquire()
            sql = """select words,id from search_words_wxh where dongfang_status=0 and category=2 limit 1  """
            result = select_data(sql)
            if result:
                for i in result:
                    sql = """update search_words_wxh set dongfang_status=1 where id=%s""" % i[1]
                    update_data(sql)
                    self.threadLock.release()
                    self.get_page(i[0])
                    sql = """update search_words_wxh set dongfang_status=2 where id=%s""" % i[1]
                    update_data(sql)
            else:
                print("已经爬取完")
                self.threadLock.release()
                break
    def get_page(self,word):

        print("*" * 50)
        print(word)
        print("*" * 50)
        time.sleep(0.5)
        self.data['name'] = word
        start = ''
        while True:
            time.sleep(0.5)
            self.data['start'] = start
            r = 10
            while True:
                if r > 60:
                    break
                try:
                    self.data['key'] = self.key
                    response = requests.post(url=self.url, data=self.data, headers=self.headers, timeout=5, verify=False)
                except Exception as result:
                    print(result)
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

            response = response.json()

            print(response)

            try:
                infos = response['data']
                for info in infos:
                    autwebid = info["id"]
                    autimageurl = info['img']
                    autfans = info['dycount']
                    autname = info['name']
                    autsub = info['dfhdesc']
                    acid = 0
                    isoriginal = info['isoriginal']
                    checktime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    autspiurl = None
                    autsumread = 0
                    autsumcomment = 0
                    auttask = 1
                    autjointime = checktime
                    auttldate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    autstate = 1
                    autdes = autsub
                    checkstate = 1
                    autindex = 'http://mini.eastday.com/toutiaoh5/page_dfh.html?dfhid=%s' % autwebid
                    apid = 11
                    articles = self.has_article(autname, autwebid)
                    if not articles:
                        print("此作者没有文章")
                        continue
                    res = self.conn.sadd('dongfang_author', autwebid)
                    if res == 1:
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
                            self.logger.info("插入成功")
                        except Exception as result:
                            print('插入失败：%s' % result)
                            self.client.rollback()
                            self.logger.error("插入失败")
                    else:
                        print('重复了')
            except Exception as result:
                print(result)
                print("%s:出错啦" % (word))
                self.logger.error("%s:出错啦" % (word))
                self.get_key()
                print("重新换一下key")
                print("新key：%s"%self.key)
                continue
            else:
                next_start = response['endid']
                if next_start == '':
                    return
                start = next_start


    def has_article(self,autname,autwebid):
        self.art_data['authorid'] = autwebid
        self.art_data['authorname'] = autname
        r = 10
        while True:
            if r > 60:
                return
            try:
                self.art_data['key'] = self.key
                art_response = requests.post(url=self.art_url, data=self.art_data, headers=self.headers, verify=False, timeout=5)
            except Exception as result:
                print(result)
                time.sleep(r)
                r += 10
                continue
            else:
                if art_response.status_code != 200:
                    time.sleep(r)
                    r += 10
                    continue
                else:
                    break
        art_response = art_response.json()
        print("art_response:%s" % art_response)
        piglist = art_response["pglist"]
        print("piglist:%s" % piglist)
        return piglist


if __name__ == '__main__':
    for i in range(3):
        thread = spider()
        time.sleep(2)
        thread.start()



