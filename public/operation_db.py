import sys
sys.path.append('../')
from public.connect_db import connect_db
from public.logger import logger


# 获取数据
def select_data(sql):
    db = connect_db()
    cursor = db.cursor()
    resultTuple = None
    try:
        cursor.execute(sql)
        resultTuple = cursor.fetchall()
        db.commit()
    except Exception as e:
        logger.error('执行SQL发生异常原因是：%s' % e)
        logger.error('SQL为：%s' % sql)
    finally:
        if db is not None:
            cursor.close()
            db.close()
    return resultTuple

def update_data(sql):
    db = connect_db()
    cursor = db.cursor()
    resultDict = {}
    try:
        cursor.execute(sql)
        db.commit()
        resultDict["rowCnt"] = cursor.rowcount
    except Exception as e:
        logger.error('执行SQL发生异常原因是：%s' % e)
        logger.error('SQL为：%s' % sql)
        resultDict["execute"] = False
    finally:
        if db is not None:
            cursor.close()
            db.close()
            resultDict["execute"] = True
            return resultDict

# 数据插入，返回主键Id
def insert_data(sql):
    db = connect_db()
    cursor = db.cursor()
    resultDict = {}
    try:
        cursor.execute(sql)
        rowId = int(cursor.lastrowid)
        db.commit()
        resultDict["rowCnt"] = cursor.rowcount
        resultDict["rowId"] = rowId
    except Exception as e:
        logger.error('执行SQL发生异常原因是：%s' % e)
        logger.error('SQL为：%s' % sql)
        resultDict["execute"] = False
    finally:
        if db is not None:
            cursor.close()
            db.close()
            resultDict["execute"] = True
            return resultDict

# 批量插入数据, 第一个参数是sql语句， 第二个参数数据类型：元祖/列表
def save_batch_data(sql,val):
    db = connect_db()
    cursor = db.cursor()
    resultDict = {}
    # sql 插入语句
    # sql = 'insert into userinfo (user, pwd, age) values ("%s", "%s", "%s") '
    # val = (('yifan1', '123', 28),
    #        ('yifan2', '123', 28),
    #        ('yifan3', '123', 28)
    #        )
    # val1 = [['yifan1', '123', 28],
    #        ['yifan2', '123', 28],
    #        ['yifan3', '123', 28]
    #        ]
    try:
        print(sql)
        cursor.executemany(sql, val)
        db.commit()
        resultDict["rowCnt"] = cursor.rowcount
    except Exception as e:
        logger.error('执行SQL发生异常 原因是：%s' % e)
        logger.error('SQL为：%s' % sql)
        db.rollback()
        resultDict["execute"] = False
    finally:
        if db is not None:
            cursor.close()
            db.close()
            resultDict["execute"] = True
            return resultDict


def insert_one(sql, val):
    """
    插入数据
    :param conn: 连接mysql
    :param sql: sql 语句
    :param val: 提交的数据
    :return:
    """
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, val)
        conn.commit()
    except Exception as e:
        logger.error('执行SQL发生异常 原因是：%s' % e)
        logger.error('SQL为：%s' % sql)
        conn.rollback()

