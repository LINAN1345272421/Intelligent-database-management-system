
import datetime
import os
import traceback
import numpy as np

from flask import Flask, render_template, request, jsonify, send_from_directory

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




if __name__ == '__main__':
    #使用numpy生成数组，得到ndarray类型
    t1=np.array([1,2,3,])
    print(t1)
    print(type(t1))
    t2=np.arange(4,12,2)#2步长
    print(t2)
    t3=np.array(range(10))
    print(t3)