
import datetime
import os
import random
import traceback
import pandas as pd
import numpy as np
import pymysql
def get_conn_mysql_name(name):
    """
    :return: 连接，游标192.168.1.102
    """
    # 创建连接
    conn = pymysql.connect(host="127.0.0.1",
                    user="root",
                    password="123456",
                    db=name,
                    charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor
def pymysql_conn(database):
    conn = pymysql.connect(
        host="127.0.0.1",  # 需要连接的数据库的ip
        port=3306,
        user="root",  # 数据库用户名
        password="123456",  # 数据库密码
        database=database
    )
    cursor = conn.cursor()
    return conn, cursor
def close_conn_mysql(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

#清洗数据存入数据库
def data_clean_save(data_clean,table_name,database_name):
    flag=1
    conn,cursor=get_conn_mysql_name(database_name)
    sql="DROP TABLE if EXISTS "+table_name+" ; "
    cursor.execute(sql)
    #判断表是否存在,存在就删除
    sql = " CREATE TABLE " + table_name + " ("
    key_0=data_clean.keys()
    key=""
    for i in key_0:
        key=key+","+i
    key=key[1:]
    j = 0
    for i in key_0:
        sql = sql + i + " TEXT  comment 'null,null',"
        j = j + 1;
    creat_sql = sql[0:-1] + ") ENGINE = InnoDB DEFAULT CHARACTER SET = utf8 COLLATE = utf8_bin;"
    print(creat_sql)
    # 获取%s
    s = ','.join(['%s' for _ in range(len(data_clean.columns))])
    # 获取values
    values = []
    for i in data_clean.values.tolist():
        values.append(i)
        # 组装insert语句
    insert_sql = 'insert into {}({}) values({})'.format(table_name, key, s)
    print(insert_sql)
    try:
        cursor.execute(creat_sql)
    except:
        traceback.print_exc()
        flag = 0
        print("表创建失败")
    # # 插入数据
    try:
        for i in values:
            cursor.execute(insert_sql, i)
            print(insert_sql)
            print(i)
        conn.commit()
    except:
        traceback.print_exc()
        flag = 0
        print("写入错误")
    close_conn_mysql(cursor, conn)
    return flag
    pass
#去除重复值
def data_clean_came(table_name,database_name):
    conn,cursor=pymysql_conn(database_name)
    qu_sql = "SELECT * FROM "+ table_name
    df = pd.read_sql_query(qu_sql, conn)
    close_conn_mysql(conn,cursor)
    num_0=df.shape[0]
    num_1=df.shape[1]
    #把‘’转换为nan
    for j in range(num_1):
        flag_list=[]
        for i in range(num_0):
            if(df.iloc[i][j]==''):
                flag_list.append(np.nan)
            else:
                flag_list.append(df.iloc[i][j])
        df.iloc[:,j]=flag_list#必须整列赋值，如果单个赋值则会失败
    data1=df.drop_duplicates(keep=False)
    data2=df.drop_duplicates(keep='first')
    data_came=data2.append(data1).drop_duplicates(keep=False)
    data_remove_came=df.drop_duplicates()
    return data_came,data_remove_came
    pass
#获取要补充的数值
def data_clean_supply_num(temp_col_not_nan,suplly_type):
    if (suplly_type == "median"):
        return temp_col_not_nan.median()
    if(suplly_type == "mean"):
        return temp_col_not_nan.mean()
#补全缺省值
def data_clean_supply(data_clean,suplly_type):
    for i in range(data_clean.shape[1]):#遍历列数
        try:
            temp_col=data_clean.iloc[:,i]#取一列
            temp_col_not_nan=temp_col[temp_col==temp_col].astype('float')#当前一列不为nan,使用布尔索引
            mean=data_clean_supply_num(temp_col_not_nan,suplly_type)
            flag_list=[]
            num=len(temp_col)
            for j in range(num):
                if(temp_col.iloc[j]!=temp_col.iloc[j]):
                    flag_list.append(mean)
                else:
                    flag_list.append(temp_col.iloc[j])
            data_clean.iloc[:,i]=flag_list# 填充均值,必须整列赋值
        except:
            pass
            #print("不是数字类型")
    return data_clean
    pass
#去除缺省行或列
def data_clean_remove(data_clean,action_on,type_on,minnum):
    return data_clean.dropna(axis=action_on, how=type_on, thresh=int(minnum))
    pass

if __name__ == '__main__':
    data_came,data_remove_came=data_clean_came('data_clean_test',"bigwork_data")
    data_clean_save(data_remove_came,"data_clean_test_clean","bigwork_update_data")
    pass