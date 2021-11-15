import codecs
import csv

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
def get_conn_mysql():
    """
    :return: 连接，游标192.168.1.102
    """
    # 创建连接
    conn = pymysql.connect(host="127.0.0.1",
                    user="root",
                    password="123456",
                    db="mongod",
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

#日期的清洗
def trans():
    data_1=pd.read_csv("word_data/result.txt")
    ip=data_1["ip"]
    time=data_1["data"]
    traffic=data_1["traffic"]
    type=data_1["type"]
    id=data_1["id"]
    day=data_1["day"]
    time_A=[]#10/Nov/2016:00:01:02
    for data in time:
        data=data.split(" ")[0]
        time_A.append(data)
    sp=[]#/拆分
    sp_2=[]#:拆分
    time_B=[]#2016-11-10 00:01:03
    for i in time_A:
        try:
            sp=i.split("/")
            sp[1]=month(sp[1])
            sp_2=sp[2].split(":")
            time_B.append(sp_2[0]+"-"+sp[1]+"-"+sp[0]+" "+sp_2[1]+":"+sp_2[2]+":"+sp_2[3])
        except:
            print("错误：")
            print(i)
            print(sp)
    # #ip,time_B,day,type,id
    # conn, cursor = get_conn_mysql()
    # for i in  range(len(ip)):
    #     try:
    #         insert_sql = "insert into resualt (ip,time_,day_,traffic,type_,id) values(%s,%s,%s,%s,%s,%s)"
    #         cursor.execute(insert_sql, [ip[i],time_B[i],day[i],traffic[i],type[i],id[i]])
    #     except:
    #         print([ip[i],time_B[i],day[i],traffic[i],type[i],id[i]])
    # conn.commit()
    # close_conn_mysql(cursor, conn)
    list = []
    for i in  range(len(ip)):
        list.append([ip[i],time_B[i],day[i],traffic[i],type[i],id[i]])
    column = ['ip', 'time', 'day','traffic','type','id']
    test = pd.DataFrame(columns=column, data=list)
    test[1:-1]
    print()
    test.to_csv('word_data/test.csv')
#月份的转换
def month(str):
    if(str=="Nov"):
        return "11"
    if(str=="Jan"):
        return "01"
    if(str=="Feb"):
        return "02"
    if(str=="Mar"):
        return "03"
    if(str=="Apr"):
        return "04"
    if(str=="May"):
        return "05"
    if(str=="Jun"):
        return "06"
    if(str=="Jul"):
        return "07"
    if(str=="Aug"):
        return "08"
    if(str=="Sept"):
        return "09"
    if(str=="Oct"):
        return "10"
    if(str=="Decan"):
        return "11"

if __name__ == '__main__':
    trans()
