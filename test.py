
import datetime
import os
import random
import traceback
import pandas as pd

import numpy as np

from flask import Flask, render_template, request, jsonify, send_from_directory

from matplotlib import pyplot as plt

import connectsql
import dictionary
import fileroot

app = Flask(__name__)
####python Flask 系统学习
#使用同一个路由,返回不同信息
#会将order_id强转为int，不成功则无法访问
@app.route("/orders/<int:order_id>")
def get_order_id(order_id):
    return 'test %s' % order_id

def test1():#numpy基础
    # 使用numpy生成数组，得到ndarray类型
    t1 = np.array([1, 2, 3, ])
    print(t1)
    print(type(t1))
    t2 = np.arange(4, 12, 2)  # 2步长
    print(t2)
    t3 = np.array(range(10))
    print(t3)

    t3.dtype  # t3中元素的数据类型
    t4 = np.array(range(1, 4), dtype="int8")  # 指定数据类型
    t4.astype("float")#修改数据类型
    t5 = np.array([random.random() for i in range(10)])  # 取小数
    t6 = np.round(t5, 2)  # 小数保留两位
    print(t2.shape)  # 形状（行数,列数）
    t5.reshape((2, 5))  # 改变形状
    t7 = np.arange(24).reshape((2, 3, 4))
    print(t7)
    t7.reshape((24,))
    # 下面俩都是二维的
    t7.reshape((1, 24))
    t7.reshape((24, 1))
    t7 = t7.reshape((4, 6))
    print(t7.shape[0], t7.shape[1])  # 行与列
    t7.flatten()  # 展开成一维度
    t7 = t7 + 2  # 广播机制，都加2
    t8 = np.arange(100, 124).reshape((4, 6))
    print(t7 + t8)  # 对应值相加
    t9 = np.arange(6)
    print(t7 - t9)  # 相同维度操作
    # 行列都不一样将无法计算
    # 在形状上包含就可运算

def test2():#numpy分片索引
    uk_file_path= "import_test/GB_video_data_numbers.csv"
    us_file_path= "import_test/US_video_data_numbers.csv"
    t1=np.loadtxt(us_file_path,delimiter=",",dtype="int",skiprows=0,unpack=False)#skiprows,跳过前n行 unpack转置
    print(t1)
    print("*"*100)
    t1[2]#取行
    t1[2:]#取多行,连续
    t1[[2,8,10]]#取多行，不连续
    t1[1,:]#[行,列]取第二行,:代表都要
    t1[:,0]#取第一例
    t1[2,3]#取第3行第4列
    t1_flag=t1[2:5,1:4]#取多行多列
    print(t1_flag)
    t1[[0,1,2],[1,2,2]]#取多个不相邻的点，[0,1] ,[1,2]，[2,2]
    t1[t1<1100]=3#将小于1100的替换为3
    np.where(t1<10,0,10)#t1<10赋值为0，否则赋值为10,三元运算符
    t1.clip(1000,20000)#将小于1000的替换为1000，将大于20000的替换为20000
    np.nan==np.nan#两个nan不一定相等,not a number
    np.count_nonzero(t1!=t1)#统计nan的个数
    #nan加任何数都是nan
    np.sum(t1_flag)#将所有数相加
    t2=np.arange(12).reshape((3,4))
    print(t2)
    #注意对“轴”的理解
    print(np.sum(t2,axis=0))#行相加
    print(np.sum(t2,axis=1))#列相加
    #numpy常用函数
    t2.sum()
    print(t2.mean(axis=0))#均值
    print(np.median(t2,axis=1))#中值
    #最大最小值
    t2.max()
    t2.min()
    np.ptp(t2)#极值
    print(t2.std())#标准差


def test3():#numpy的nan值替换为列平均值
    t1=np.arange(12).reshape((3,4)).astype("float")
    t1[1,2:]=np.nan
    print("t1:")
    print(t1)
    for i in range(t1.shape[1]):#遍历列数
        temp_col=t1[:,i]#取一列
        temp_col_not_nan=temp_col[temp_col==temp_col]#当前一列不为nan,使用布尔索引
        print(temp_col==temp_col)
        print("temp_col_not_nan")
        print(temp_col_not_nan)
        temp_col[np.isnan(temp_col)]=temp_col_not_nan.mean()#将均值赋值给nan
        print("temp_col")
        print(temp_col)
        print("*"*100)

def test4():#数组的拼接
    t1=np.arange(12).reshape((3,4))
    t2=np.arange(12,24).reshape((3,4))
    print("t1")
    print(t1)
    print("t2")
    print(t2)
    print(np.vstack((t1,t2)))#竖直拼接
    print(np.hstack((t1,t2)))#水平拼接
    print("*"*100)
    t1[[1,2],:]=t1[[2,1],:]#行交换
    print(t1)
    t1[:,[0,2]]=t1[:,[2,0]]#列交换
    print(t1)
    #获取最大值最小值的位置
    np.argmax(t1,axis=0)
    np.argmin(t1,axis=1)
    #创建全为0的数组
    np.zeros((3,4))
    #全为1的数组
    np.ones((3,4))
    #创建对角线为1的正方形数组
    np.eye(3)
    # t1=t2.copy() 复制，相互不影响

def test5():#np的随机函数
    np.random.rand(2,3)#产生2行3列的均匀分布的随机数组
    np.random.randn(2,3)#标准正态分布数组
    np.random.randint(10,20,(3,4))#范围[10，20)，三行四列的随机整数数组
    np.random.uniform(10,20,(3,4))#产生均匀分布数组
    np.random.seed(10)#设置随机种子


def test1_pandas():#pandas基础
    t = pd.Series([1, 2, 3, 4, 5, 6, 7])  # Series 一维，带标签数组
    print(t)
    t2 = pd.Series([1, 2, 3, 4, 5], index=list("abcde"))  # 指定标签
    print(t2)
    temp_dict = {"name": "xiaohong", "age": 30, "tel": 10086}
    t3 = pd.Series(temp_dict)  # 通过字典创建
    print(t3)
    t3.index  # 索引
    t3.values  # 值

    # DataFrame
    t3 = pd.DataFrame(np.arange(12).reshape(3, 4))
    print(t3)
    # DataFrame对象既有行索引，又有列索引
    # 行索引，表明不同行，横向索引，叫index，0轴，axis=0
    # 列索引，表名不同列，纵向索引，叫columns，1轴，axis=1
    # ndim 维度属性
    t1 = pd.DataFrame(np.arange(12).reshape(3, 4), index=list("abc"), columns=list("WXYZ"))  # 指定行列的索引
    d1 = {"name": ["xiaoming", "xioahong"], "age": [10, 20], "tel": [100086, 10085]}
    print(pd.DataFrame(d1))  # 通过字典创建
    d2 = [{"name": "xiaohong", "age": 10, "tel": 10086}, {"name": "xiaownag", "age": 10, "tel": 10085}]
    pd.DataFrame(d2)
    t1.head(3)  # 显示头几行
    t1.tail(3)  # 显示末尾几行
    t1.info()  # 展示df的概览
    file_path = "import_test/tttt.txt"
    df = pd.read_csv(file_path)
    df_clean=pd.DataFrame(df[2:],columns=list(["test1","test2","test3","test4"]))
    df_clean.apply(pd.to_numeric, errors='ignore')
    for i in list(["test1","test2","test3","test4"]):
        try:
            df_clean[i] = df_clean[i].astype(float)
        except:
            print("数据类型不符合")
    print(df_clean.describe())
    file_path = "import_test/tttt1.txt"
    df2 = pd.read_csv(file_path)
    print(df2.describe())  # 快速进行统计：count,mean,std,min
    pass

def test_pandas2():#pandas索引
    # pandas索引
    # loc通过标签获取
    t4 = pd.DataFrame(np.arange(12).reshape(3, 4), index=list("abc"), columns=list("WXYZ"))
    print(t4)
    print(t4.loc["a", "Z"])
    print(t4.loc["a", :])
    print(t4.loc[:, "Y"])
    print(t4.loc[["a", "c"], :])
    print(t4.loc[["a", "b"], ["W", "Z"]])
    # iloc通过位置获取
    print(t4.iloc[1, :])
    # 布尔索引
    print(t4[t4["W"] > 2])  # &,|
    # 缺失值处理
    t4.iloc[1] = np.nan
    t4.iloc[1, 2] = 2.0
    print(t4)
    print(pd.isnull(t4))  # 是否为空
    print(pd.notnull(t4))  # 是否不为空
    # 删除
    print(t4[pd.notnull(t4.iloc[:, 0])])  # 把nan所在的行去掉
    t4.dropna(axis=0, how="all", inplace=False)  # 删除nan所在行,all全为nan则删掉，any只要有一个就删掉,inplace是否对源数据修改
    # 填充
    t4.fillna(t4.mean())  # 填充均值
    pass


def test_pandas():#pandas案例
    file_path= "import_test/IMDB-Movie-Data.csv"
    df=pd.read_csv(file_path)
    print(df.head(1))
    print(df.info())
    #rating runtime分布情况
    #选择图形,直方图
    #准备数据
    runtime_data=df["Runtime (Minutes)"].values
    max_runtime=runtime_data.max()
    min_runtime=runtime_data.min()
    # 计算组距
    num_bin=(max_runtime-min_runtime)//5
    #设置图形的大小
    # plt.figure(figsize=(20,8),dpi=80)
    # plt.hist(runtime_data,num_bin)
    # plt.xticks(range(min_runtime,max_runtime+5,5))
    # plt.show()


    #获取电影平均分
    print(df["Rating"].mean())
    #获取导演人数
    print(len(set(df["Director"].tolist())))#set函数创建一个无序不重复元素集
    print(len(df["Director"].unique()))#unique函数创建不重复的列表
    #获取演员的人数
    temp_actors_list=df["Actors"].str.split(", ").tolist()
    print(temp_actors_list)
    actors_list=[i for j in temp_actors_list for i in j]
    actors_num=len(set(actors_list))
    print(actors_num)

    #电影分类
    #统计分类列表
    temp_list=df["Genre"].str.split(",").tolist()
    genre_list=list(set([i for j in temp_list for i in j] ))
    #构造全为0的数组
    zeros_df=pd.DataFrame(np.zeros((df.shape[0],len(genre_list))),columns=genre_list)
    print(zeros_df)
    #给每个顶电影出现的位置赋值为1
    for i in range(df.shape[0]):
        #zeros_df.loc[0,["Sci-fi","Mucical"]]=1
        zeros_df.loc[i,temp_list[i]]=1

    print(zeros_df.head(3))
    #统计每个分类电影数量和
    genre_count=zeros_df.sum(axis=0)
    print(genre_count)
    #排序
    genre_count=genre_count.sort_values()
    print(genre_count)
    pass

if __name__ == '__main__':
    test1_pandas()
    pass


