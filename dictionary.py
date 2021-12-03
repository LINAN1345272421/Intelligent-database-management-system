import pandas as pd
import jieba

import string
import time
import traceback

import pymysql
import requests
import re

from bs4 import BeautifulSoup
from flask import json
import nltk
from nltk.corpus import brown

#数据库的连接与查询
import fileroot


def get_conn_mysql():
    """
    :return: 连接，游标192.168.1.102
    """
    # 创建连接
    conn = pymysql.connect(host="127.0.0.1",
                    user="root",
                    password="123456",
                    db="bigwork_data",
                    charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor
def close_conn_mysql(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()
def query_mysql(sql,*args):
    """
    封装通用查询
    :param sql:
    :param args:
    :return: 返回查询结果以((),(),)形式
    """
    conn,cursor = get_conn_mysql();
    cursor.execute(sql)
    res=cursor.fetchall()
    close_conn_mysql(conn,cursor)
    return res
def pymysql_conn():
    conn = pymysql.connect(
        host="127.0.0.1",  # 需要连接的数据库的ip
        port=3306,
        user="root",  # 数据库用户名
        password="123456",  # 数据库密码
        database="bigwork_data"
    )
    cursor = conn.cursor()
    return conn, cursor

#获取表的数据字典
def get_dictionary(name_table,database_name):
    #中文名，英文名，数据类型，单位
    # select column_name,column_comment ,data_type,CHARACTER_MAXIMUM_LENGTH,COLUMN_DEFAULT
    # from information_schema.columns
    # where table_name='表名' and table_schema='bigwork_data'
    #英文名，中文名，字段类型，字段长度，缺省值，单位在中文名中以逗号隔开
    sql="select column_name,column_comment ,data_type,CHARACTER_MAXIMUM_LENGTH,COLUMN_DEFAULT " \
        "from information_schema.columns " \
        "where table_name='"+name_table+"' and table_schema='"+database_name+"'"
    res = query_mysql(sql)
    return res
    pass
#获取表的内容
def get_table_details(name_table,database_name):
    #中文名，英文名，数据类型，单位
    # select column_name,column_comment ,data_type,CHARACTER_MAXIMUM_LENGTH,COLUMN_DEFAULT
    # from information_schema.columns
    # where table_name='表名' and table_schema='bigwork_data'
    #英文名，中文名，字段类型，字段长度，缺省值，单位在数据的第一行
    sql="select * from "+name_table
    res = query_mysql(sql)
    return res
    pass
#获取表键值
def get_table_details_key(name_table,database_name):
    sql = "select column_name,column_comment " \
          "from information_schema.columns " \
          "where table_name='" + name_table + "' and table_schema='" + database_name + "'"
    res = query_mysql(sql)
    return res
#获取快速分析的key
def get_table_clean(name_table,database_name):
    #pandas读取数据库
    conn, cursor=pymysql_conn()
    qu_sql = "SELECT * FROM "+name_table
    df = pd.read_sql_query(qu_sql, conn)
    #获取key值（china，english）
    keys_or=get_table_details_key(name_table,database_name)
    #获取keyEnglish
    keys=[]
    for i in keys_or:
        keys.append(i[0])
    #转换数据类型
    print("数据快速分析"+name_table)
    for i in keys:
        try:
            df[i] = df[i].astype(float)
        except:
            print("数据类型不符合")
    df_describe=df.describe()
    print(df_describe)
    return df_describe.keys(),df_describe.index,df_describe.values
    pass

#获取表的信息
def get_table_data():
    #表名，数据库，行数，创建实际
    sql="SELECT TABLE_NAME,TABLE_SCHEMA,TABLE_ROWS,CREATE_TIME " \
        "FROM information_schema.TABLES " \
        "where  TABLE_SCHEMA='bigwork_data';"
    res = query_mysql(sql)
    return res
    pass


#修改数据字典
#ALTER TABLE `bigwork_data`.`test_dictionary` CHANGE COLUMN `id` `id` varchar(255) NOT NULL DEFAULT '#' COMMENT '序号' ;
#update bigwork_data.test_dictionary set id = '0' where id= '0'
def update_dictionary(table_name,database_name,key_china,key_type,key_english,key_long,key_null,key_unit,key_english_0):
    flag=1
    sql="ALTER TABLE `"+database_name+"`.`"+table_name+"` " \
        "CHANGE COLUMN `"+key_english_0+"` `"+key_english+"` "+key_type+"("+key_long+")"+" NOT NULL DEFAULT '"+key_null+"' COMMENT '"+key_china+","+key_unit+"' ;"
    conn, cursor = get_conn_mysql()
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()
        flag = 0
        print("写入错误")
    print("数据字典修改：")
    print(sql)
    close_conn_mysql(cursor, conn)
    return flag
#删除数据字典
#ALTER TABLE `bigwork_data`.`test_dictionary` DROP COLUMN `name`;
def delete_dictionary(table_name,database_name,clumn):
    flag=1
    conn, cursor = get_conn_mysql()
    sql="ALTER TABLE `"+database_name+"`.`"+table_name+"` DROP COLUMN `"+clumn+"`"
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()
        flag = 0
        print("写入错误")
    print("数据字典删除：")
    print(sql)
    close_conn_mysql(cursor, conn)
    return flag
#数据字典添加
#ALTER TABLE `bigwork_data`.`test_dictionary` ADD COLUMN `name` VARCHAR(45) NOT NULL DEFAULT '#' COMMENT '姓名' ;
def add_dictionary(table_name,database_name,key_china,key_type,key_english,key_long,key_null,key_unit):
    flag=1
    sql="ALTER TABLE `"+database_name+"`.`"+table_name+\
        "` ADD COLUMN `"+key_english+"` "+key_type+"("+key_long+")"+" NOT NULL DEFAULT '"+key_null+"' COMMENT '"+key_china+","+key_unit+"'"
    conn, cursor = get_conn_mysql()
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()
        flag = 0
        print("写入错误")
    print("数据字典添加：")
    print(sql)
    close_conn_mysql(cursor, conn)
    return flag


#表的删除
def delete_table(table_name):
    flag = 1
    conn, cursor = get_conn_mysql()
    sql="DROP TABLE "+table_name
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()
        flag = 0
        print("写入错误")
    print("表的删除：")
    print(sql)
    close_conn_mysql(cursor, conn)
    return flag
    pass


if __name__ == '__main__':
    # update_dictionary("test_dictionary","bigwork_data","标号","int","id","11","0","0","id","1")
    get_table_clean("test_dictionary","bigwork_data")
    pass