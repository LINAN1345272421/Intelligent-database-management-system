import pandas as pd
import jieba

import datetime
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

#数据库的连接查询
def get_conn_mysql():
    """
    :return: 连接，游标192.168.1.102
    """
    # 创建连接
    conn = pymysql.connect(host="127.0.0.1",
                    user="root",
                    password="123456",
                    db="bigwork_root",
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


#修改文件状态
def file_update_state(file_name,file_state):
    flag=1;
    conn, cursor = get_conn_mysql()
    sql="update root_file set file_state='"+file_state+"' where file_name='"+file_name+"'"
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()
        flag=0
        print("写入错误")
    close_conn_mysql(cursor, conn)
    return flag
#将文件的基本信息写入数据库
def file_root(file_name,file_time,file_type,file_size,user_id):
    flag=1;
    conn, cursor = get_conn_mysql()
    #将文件的file_name(文件名),file_time(上传时间),file_type(文件类型),file_size(文件大小)
    #写入数据库
    sql="insert into root_file (file_name,file_time,file_type,file_size,user_id) value(%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql,[file_name,file_time,file_type,file_size,user_id])
        conn.commit()
    except:
        traceback.print_exc()
        flag=0
        print("写入错误")
    close_conn_mysql(cursor, conn)
    return flag
#文件删除
def delete_file(file_name):
    flag=1
    conn, cursor = get_conn_mysql()
    sql="delete from root_file where file_name='"+file_name+"'"
    try:
        cursor.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()
        flag=0
        print("写入错误")
    print("文件删除")
    print(sql)
    close_conn_mysql(cursor, conn)
    return flag


#查找文件通过文件名，文件名为主键
def find_filedata_filename(file_name):
    conn, cursor = get_conn_mysql()
    sql="select * from root_file where file_name='"+file_name+"'"
    res = query_mysql(sql)
    print("文件查询：")
    print(res)
    return res
#文件状态列表
def file_state_list():
    sql="select * from root_file "
    res = query_mysql(sql)
    print("文件状态列表：")
    print(res)
    return res

if __name__ == '__main__':
    find_filedata_filename("nihao")