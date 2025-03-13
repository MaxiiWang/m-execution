import pymysql
from datetime import datetime

from config import Config


def write_to_mariaDB(table, data:dict):
    mariaDB_connection = pymysql.connect(host=Config.MYSQL_HOST, port=Config.MYSQL_PORT, user=Config.MYSQL_USER, password=Config.MYSQL_PWD, database=Config.DB_NAME)

    cursor = mariaDB_connection.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, list(data.values()))
    id = cursor.lastrowid
    mariaDB_connection.commit()
    cursor.close()
    mariaDB_connection.close()

    return {"total": 1, "data": [id]}

def write_many_to_mariaDB(table, data:list):
    mariaDB_connection = pymysql.connect(host=Config.MYSQL_HOST, port=Config.MYSQL_PORT, user=Config.MYSQL_USER, password=Config.MYSQL_PWD, database=Config.DB_NAME)

    cursor = mariaDB_connection.cursor()
    columns = ', '.join(data[0].keys())
    placeholders = ', '.join(['%s'] * len(data[0]))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'

    ret = {
        "total":0,
        "data":[]
    }
    for item in data:
        cursor.execute(sql, list(item.values()))
        ret['total'] += 1
        ret['data'].append(cursor.lastrowid)

    mariaDB_connection.commit()
    cursor.close()
    mariaDB_connection.close()

    return ret

def read_from_mariaDB(table, columns="*", condition=None, limit=None, skip=None, order_by=None, desc=False):
    mariaDB_connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PWD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor  # 使用 DictCursor
    )
    cursor = mariaDB_connection.cursor()
    if not condition:
        sql = f'SELECT {select} FROM {table}'
        count_sql = f'SELECT COUNT(*) FROM {table}'
    else:
        condition = ' AND '.join([f'{k} = "{v}"' for k, v in condition.items()])
        sql = f'SELECT {columns} FROM {table} WHERE {condition}'
        count_sql = f'SELECT COUNT(*) FROM {table} WHERE {condition}'
    
    if order_by:
        sql += f' ORDER BY {order_by}'
        if desc:
            sql += ' DESC'
    if limit:
        if skip:
            sql += f' LIMIT {skip}, {limit}'
        else:
            sql += f' LIMIT {limit}'

    print('sql:', sql)
    cursor.execute(sql)
    mariaDB_connection.commit()
    result = cursor.fetchall()

    cursor.execute(count_sql)
    mariaDB_connection.commit()
    count = cursor.fetchone()['COUNT(*)']

    cursor.close()
    mariaDB_connection.close()

    return {"total": count, "data":result}

def update_mariaDB(table, data: dict, condition):
    mariaDB_connection = pymysql.connect(host=Config.MYSQL_HOST, port=Config.MYSQL_PORT, user=Config.MYSQL_USER, password=Config.MYSQL_PWD, database=Config.DB_NAME)

    cursor = mariaDB_connection.cursor()

    # 拼接 SET 语句
    # value_str = ", ".join([f"{k} = {v}" for k, v in data.items()])
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = f'"{value}"'
        elif isinstance(value, datetime):
            data[key] = f'"{value.strftime("%Y-%m-%d %H:%M:%S")}"'
        else:
            data[key] = str(value)
    value_str = ", ".join([f"{k} = {v}" for k, v in data.items()])
    
    for key, value in condition.items():
        if isinstance(value, str):
            condition[key] = f'"{value}"'
        elif isinstance(value, datetime):
            condition[key] = f'"{value.strftime("%Y-%m-%d %H:%M:%S")}"'
        else:
            condition[key] = str(value)

    condition = ' AND '.join([f'{k} = {v}' for k, v in condition.items()])

    # 生成最终的 SQL 语句
    sql = f'UPDATE {table} SET {value_str} WHERE {condition}'

    print('update sql:', sql)

    # 执行 SQL 语句
    cursor.execute(sql)
    mariaDB_connection.commit()
    # 关闭连接
    cursor.close()
    mariaDB_connection.close()

def delete_from_mariaDB(table, condition):
    mariaDB_connection = pymysql.connect(host=Config.MYSQL_HOST, port=Config.MYSQL_PORT, user=Config.MYSQL_USER, password=Config.MYSQL_PWD, database=Config.DB_NAME)

    cursor = mariaDB_connection.cursor()

    condition = ' AND '.join([f'{k} = "{v}"' for k, v in condition.items()])

    sql = 'delete from ' + table + ' where ' + str(condition)
    print('delete sql:', sql)
    cursor.execute(sql)
    mariaDB_connection.commit()

    # 关闭连接
    cursor.close()
    mariaDB_connection.close()

