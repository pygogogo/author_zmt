#@Time    :2019/9/29 17:18
#@Author  :wuxinghui 
#@FileName: qingbo_account.py
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import faker
from public.operation_db import select_data, update_data, save_batch_data


"""
功能描述：获取账号信息，category = 1高级账号，category = 2 普通账号
"""


def account_select_id():
    sql_select_cookie_account =  """SELECT id,cookie,useCount FROM cookie_wxh WHERE   status = 0 and platform='toutiao' order by useCount asc limit 1"""
    resultTuple = select_data(sql_select_cookie_account)
    if len(resultTuple) == 0:
        return

    useCount = resultTuple[0][2] + 1
    sql_update_cookie_account_useCount = 'UPDATE  cookie_wxh set useCount=%d where id=%d' % (
    useCount, resultTuple[0][0])
    update_data(sql_update_cookie_account_useCount)
    #返回id和cookie
    return resultTuple[0][0], resultTuple[0][1]


def account_hearder_id():
    cookie_id = account_select_id()
    if not cookie_id:
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'referer': 'https://www.toutiao.com/search/?keyword=123',}
    #'cookie': 'tt_webid=6746198434971895304; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6746198434971895304; __tasessionId=dtua5m5g31570721740320; s_v_web_id=14faad0910856371aff16507c019e7f1; csrftoken=7aee0cc77847e9c2d22655e086353ff2' }

    return cookie_id[0],headers

if __name__ == "__main__":
    account_select_id()