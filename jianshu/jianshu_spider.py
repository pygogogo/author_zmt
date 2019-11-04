# -- coding:gbk --
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import time
import re
import datetime
from lxml import etree
from   jianshu1.cookie import get_cookie,get_cookie_csrf
import pymysql
from redis import Redis
from public.operation_db import select_data,update_data
import random


import logging
logger = logging.getLogger('author_push')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('jianshu.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


client = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com", port=3306,
                         password="YZdagKAGawe132sazljjQklf", user="spider", db="spider")
cursor = client.cursor()
conn = Redis(host='47.101.128.5',port=6379)

start_time = time.time()


def get_words():
    global start_time
    while True:
        end_time = time.time()
        if end_time - start_time > 20 * 60:
            print('程序休眠中')
            time.sleep(5*60)
            start_time = end_time
        sql = """select words,id from search_words_wxh where jianshu_status=0 and category=2 limit 1"""
        result = select_data(sql)
        if result:
            for i in result:
                sql = """update search_words_wxh set jianshu_status=1 where id=%s""" % i[1]
                update_data(sql)
                spider(i[0])
                sql = """update search_words_wxh set jianshu_status=2 where id=%s""" % i[1]
                update_data(sql)
        else:
            print("已经爬取完")
            break

def spider(word):
    infos = {
            'type': 'user',
            'order_by': 'default'
        }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Referer': 'https://www.jianshu.com',
        'cookie': '__yadk_uid=ZhHMTBpRoCtSRxBV2Y3QRdm95Xfl7YCb; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216cf070bf444f2-0da09684a78ad7-5373e62-2073600-16cf070bf45aee%22%2C%22%24device_id%22%3A%2216cf070bf444f2-0da09684a78ad7-5373e62-2073600-16cf070bf45aee%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_utm_source%22%3A%22desktop%22%2C%22%24latest_utm_medium%22%3A%22search-recent%22%7D%7D; read_mode=day; default_font=font2; locale=zh-CN; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1571900705,1571901650,1571902524,1571903610; signin_redirect=https%3A%2F%2Fwww.jianshu.com%2Fsearch%3Fq%3DPython%26utm_source%3Ddesktop%26utm_medium%3Dsearch-recent; _m7e_session_core=fd9c08def60e0138949273447a2f6cf1; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1571903612',
        'x-csrf-token': 'ViTEdqx44igTnNSMDdJOawDZmewPU5lZrFLASiG3mImLkD5H7+BvkyllT2W8AMBg3CPzrqOWUlpyFSW2brPFNw==',
          'Connection':'close'
    }

    url = 'https://www.jianshu.com/search/do'

    print(word)
    print(type(word))
    for i in range(1,10000):
        time.sleep(random.randint(3,8))
        infos['q'] = word
        infos['page'] = str(i)
        while True:
            r = 10
            if r > 60:
                break
            try:
                response = requests.post(url=url,headers=headers,data=infos,timeout=20)
                print(response.status_code)
                response = response.json()
                datas = response['entries']

            except requests.exceptions.ReadTimeout:
                print('请求个人主页超时')
                time.sleep(r)
                r += 10
                continue
            except Exception as result:
                print('请求1其他错误%s' % result)
                time.sleep(r)
                r += 10
                cookie,csrf = get_cookie_csrf('https://www.jianshu.com')
                headers['cookie'],headers['x-csrf-token'] = cookie,csrf
                continue
            else:
                print('访问正常')
                break


        print(datas)
        if datas:
            for data in datas:
                print("*"*20)
                autname = data['nickname']
                autwebid = data['slug']
                autindex = 'https://www.jianshu.com/u/' + data['slug']
                autimageurl = data['avatar_url']
                autfans = data['followers_count']
                article_num = data['public_notes_count']
                print(article_num)
                if article_num == 0:
                    print('此作者没有文章:%s'%autname)
                    continue
                apid = '14'
                acid = 0
                autspiurl = None
                autsumcomment = 0
                autsumread = 0
                auttask = 1
                checktime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                autjointime =checktime
                auttldate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                autstate = 1
                isoriginal = None
                checkstate = 1

                pic = (apid, autname,  autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate,checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans)

                response = conn.sadd('js_author',autwebid)
                if response == 1:
                    get_sub(autindex,pic)
                else:
                    print('%s重复了'%autname)
                    break
        else:
            break

def get_sub(url,pic):
    time.sleep(random.randint(1,2))
    apid,autname, autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans = pic
    headers = {
        'Use-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Connection': 'close'
    }
    r = 10
    while True:
        if r >60:
            break
        try:
            response = requests.get(url=url,headers=headers,timeout=10)
        except requests.exceptions.ReadTimeout:
            print('请求个人主页超时')
            time.sleep(r)
            r +=10
            continue
        except Exception as result:
            print('请求2其他错误%s'%result)
            time.sleep(r)
            r += 10
            continue
        else:
            break

    try:
        html = etree.HTML(response.text)
    except Exception as result:
        print(result)
        return
    else:
        autsub = html.xpath("//div[@class='js-intro']/text()")
        if len(autsub) != 0:
            autsub = autsub[0]
        else:
            autsub = ''

        autdes = autsub
        # dics = {'autname': autname, 'autwebid': autwebid, 'autindex': autindex, 'autimageurl': autimageurl,
        #        'autfans': autfans, 'apid': apid, 'checktime': checktime, 'acid': acid,
        #        'autspiurl': autspiurl,
        #        'autsumcomment': autsumcomment, 'autsumread': autsumread, 'auttask': auttask,
        #        'autjointime': autjointime, 'auttldate': auttldate, 'autstate': autstate,
        #        'isoriginal': isoriginal,
        #        'checkstate': checkstate, 'autdes': autdes, 'autsub': autsub}
        # print(dics)

        try:
            sql = '''insert into author_push(apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate, auttask, autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment, isoriginal, autfans) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql, (
                apid, autname, autsub, autindex, autimageurl, autjointime, checktime, auttldate,
                auttask,
                autstate, autdes, checkstate, autspiurl, acid, autwebid, autsumread, autsumcomment,
                isoriginal,
                autfans))
            client.commit()
            print('插入成功')
            logger.info('插入成功')
        except Exception as result:
            print('插入失败：%s' % result)
            client.rollback()
            logger.error('插入失败')
            logger.error(result)




if __name__ == '__main__':
    get_words()