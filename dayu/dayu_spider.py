import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import re
import json
from lxml import etree
import datetime
import time
import random
from redis import Redis
import pymysql
from public.operation_db import select_data,update_data
import threading

import logging
logger = logging.getLogger('author_push')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('dayu.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)



proxies = {'http': '192.168.10.244:8088'}


class daYuSpider(object):
    formdata = {
        'method': 'Subscribe.feed',
        'format': 'json',
        'page': '1',
        'callback': 'jsonp1',
        '_t': '1571453965610'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1; PAR-AL00 Build/HUAWEIPAR-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools',
        'Connection': 'close'
    }
    art_data = {
        'uc_param_str': 'frdnpfvecpntgibiniprdswiut',
        'app': 'ucweb',
        'sub_type': 'wm',
        'b_version': '0.4',
        'errCode': '2',
        'errMsg': 'ucapi.invoke not exsit, should load in UCBrowser!',
        'ut': 'AAQIjAIAHMOf1SRqpVQusBN1ZfoG/pbUY1QxS7YNysQRmg==',
        'col_cont_src': 'all',
        'from': 'msg',
        'size': '10',
        'max_pos': '',
    }
    def __init__(self):
        self.conn = Redis(host='47.101.128.5', port=6379)
        self.start_time = time.time()
        self.url = 'https://m.sm.cn/api/rest'
        self.client = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com", port=3306,
                                 password="YZdagKAGawe132sazljjQklf", user="spider", db="spider")
        self.cursor = self.client.cursor()

    def __del__(self):
        print("关闭数据库")
        self.client.close()

    def run(self):
        while True:
            end_time = time.time()
            if end_time - self.start_time > 15 * 60:
                print('程序休眠中')
                time.sleep(90)
                self.start_time = end_time
            sql = """select words,id from search_words_wxh where dayu_status=0 and category=2 limit 1"""
            result = select_data(sql)
            if result:
                for i in result:
                    sql = """update search_words_wxh set dayu_status=1 where id=%s""" % i[1]
                    update_data(sql)
                    self.spider(i[0])
                    sql = """update search_words_wxh set dayu_status=2 where id=%s""" % i[1]
                    update_data(sql)
            else:
                print("已经爬取完")
                break

    def spider(self,word):
        print("*"*50)
        print(word)
        print("*"*50)
        self.formdata['q'] = word
        for i in range(1,1000):
            time.sleep(1)
            self.formdata['page'] = str(i)
            r = 10
            while True:
                if r > 60:
                    print('超过六次了')
                    break
                try:
                    response = requests.get(url=self.url, headers=self.headers, params=self.formdata, timeout=20)
                except Exception as result:
                    print('请求2出现错误:%s' % result)
                    logger.error('请求2出现错误:%s' % result)
                    time.sleep(r)
                    r += 10
                    continue
                else:
                    if response.status_code !=200:
                        print("请求1code:%s"%response.status_code)
                        time.sleep(r)
                        r+=10
                        continue
                    else:
                        break

            print(response.text)
            datas = re.findall(r'jsonp1\((.*)\)',response.text,re.DOTALL)[0]
            datas = json.loads(datas)
            datas = datas['data']
            if datas:
                html=datas['feed_html']
                print(html)
            else:
                break
            print(html)
            html = etree.HTML(html)
            divs = html.xpath("//div[@class='cell-wrapper']")
            for div in divs:
                title = div.xpath(".//p[@class='title']//text()")[:-1]
                autname = ''.join(title)
                autindex = div.xpath("./a/@href")[0]
                autimageurl = div.xpath(".//div[@class='img']/@data-image")[0]
                autsub = div.xpath(".//p[@class='summary']/text()")
                print(autsub)
                if autsub:
                    autsub = ''.join(autsub)
                else:
                    autsub=''
                info = div.xpath('.//div[@class="icons"]//text()')
                info = ''.join(info)
                autfans = re.findall(r"(\d*)人",info,re.DOTALL)
                if autfans:
                    print(autfans)
                    autfans = autfans[0]
                    if '万' in autfans:
                        autfans = autfans.replace('万','')
                        autfans = int(autfans)*10000
                    else:
                        pass
                else:
                    autfans=0
                print(autfans)
                autwebid = re.findall(r"wmId%22:%22(.*?)%22",autindex,re.DOTALL)[0]
                apid=1
                acid=0
                autspiurl = None
                autsumread = 0
                autsumcomment = 0
                auttask = 1
                checktime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                autjointime = checktime
                auttldate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                autstate = 1
                isoriginal = None
                checkstate = 1
                autdes = autsub
                response = self.conn.sadd('author',autwebid)

                if response == 1:
                    msgs = self.has_article(autwebid)
                    if not msgs:
                        print('此作者没有文章:%s' % autname)
                        continue
                    try:
                        sql = '''insert into author_push(apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                        self.cursor.execute(sql, (
                            apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate,
                            auttask,
                            autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment,
                            isoriginal,
                            autfans))
                        self.client.commit()
                        logger.info("插入数据库成功")
                        print('插入成功')
                    except Exception as result:
                        print('插入失败：%s' % result)
                        self.client.rollback()
                        logger.error("插入数据库失败原因：%s" % result)
                else:
                    print('重复了')

    def has_article(self,autwebid):
        url = 'https://upbigsubs-api.uc.cn/api/bigsubs/wm/%s/msgs'%autwebid
        r = 10
        while True:
            if r > 60:
                print('超过六次了')
                return
            try:
                art_response = requests.get(url=url,params=self.art_data,proxies=proxies,headers=self.headers,timeout=10)
            except Exception as result:
                print('请求1出现错误:%s'%result)
                logger.error('请求1出现错误:%s' % result)
                time.sleep(r)
                r += 10
                continue
            else:
                if art_response.status_code != 200:
                    print(art_response.status_code)
                    time.sleep(r)
                    r += 10
                    continue
                else:
                    break
        art_response = art_response.json()
        msgs = art_response['data']['list']
        return msgs


if __name__ == '__main__':
    for i in range(3):
        thread = daYuSpider()
        time.sleep(1)
        thread.start()





