import sys
sys.path.append('../')
import pymysql


def connect_db():
    """
    连接mysql数据库
    :return: 数据库连接以及游标
    """

    conn = pymysql.connect(host="rm-uf633qqib19ed07z9oo.mysql.rds.aliyuncs.com",
                           user='spider',
                           password="YZdagKAGawe132sazljjQklf",
                           db='spider',
                           charset="utf8mb4")

    return conn
