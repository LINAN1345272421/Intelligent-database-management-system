import datetime
import os
import traceback

from flask import Flask, render_template, request, jsonify, send_from_directory, session

import connectsql
import dictionary
import fileroot

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(30)

#此部分为URL跳转配置
@app.route('/index')
def hello_world_show():
    session['user_id'] = '20194073'
    return render_template("index.html")
@app.route('/table_list')
def hello_world_show_2():
    return render_template("table_list.html")
@app.route('/look_dictionary')
def hello_world_show_3():
    table_name=request.values.get("table_name")
    database_name=request.values.get("database_name")
    return render_template("data_dictionary.html",table_name=table_name,database_name=database_name)
@app.route('/table_details')
def hello_world_show_4():
    table_name=request.values.get("table_name")
    database_name=request.values.get("database_name")
    english_china=[]
    english_china=dictionary.get_table_details_key(table_name,database_name)
    return render_template("table_details.html",table_name=table_name,database_name=database_name)
@app.route('/file_list')
def hello_world_show_5():
    return render_template("file_list.html")
@app.route('/look_list')
def hello_world_show_6():
    return render_template("look_list.html")
@app.route('/data_clean')
def hello_world_show7():
    return render_template("data_clean.html")
#此部分为URL跳转配置




######文件导入导出
china_row_0=0#中文名 行
english_row_0=0#英文名 行
unit_row_0=0#单位 行
type_0=0#1追加，0覆盖
#格式设置
@app.route("/set_rows")
def set_rows():
    #使用全局变量赋值
    global china_row_0
    china_row_0=request.values.get("china_row")
    global english_row_0
    english_row_0 = request.values.get("english_row")
    global unit_row_0
    unit_row_0 = request.values.get("unit_row")
    global type_0
    type_0 = request.values.get("type")
    return jsonify({"flag":1})
#文件大小转换
def hum_convert(value):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size
#文件导入
#json格式
# {
#   "code": 0,
#   "msg": "",
#   "count": 1000,
#   "data": [{}, {}]
# }
@app.route('/import_data', methods=['POST', 'GET'])
def import_data():
    #用户
    user_id=session['user_id']
    #设置flag以确定是否写入成功
    flag=0;
    #返回码含义：0上传失败，1上传成功，2上传类型不符，但是还会上传，传到test_data,3文件名重复已覆盖，4文件名重复以追加5填写格式
    #获取文件
    the_file = request.files.get("file")
    #获取文件基本信息
    file_type=the_file.filename.split(".")[1]
    file_name=the_file.filename.split(".")[0]
    file_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_data = fileroot.find_filedata_filename(file_name)
    #判断格式是否设置
    if(china_row_0==english_row_0==unit_row_0==0):
        return jsonify({"code": 5, "msg": "", "data": ""})
    else:#填写后根据文件类型上传
        #使用全局变量
        china_row_flag=china_row_0
        english_row_flag =  english_row_0
        unit_row_flag = unit_row_0
        type_flag=type_0
        flag_came=0#判断文件是否重复
        if(fileroot.find_filedata_filename(file_name)==()):
            flag_came=0
        else:
            flag_came=1
        print("文件上传配置:")
        print(china_row_flag,english_row_flag,unit_row_flag,type_flag)
        if(file_type=="csv" or file_type=="txt"):#1.保存文件2.写入文件状态表3.导入数据库4.修改状态
            # 保存文件到指定路径
            the_file.save("import_csv/" + the_file.filename)
            file_size=os.path.getsize("import_csv/"+the_file.filename)
            # 记录文件基本信息
            if(flag_came==0):
                fileroot.file_root(file_name,file_time,file_type,""+hum_convert(file_size),user_id)
                fileroot.file_update_state(file_name,"已上传")
            print("文件类型："+file_type+"，文件大小："+""+hum_convert(file_size)+",上传时间："+file_time+",文件名："+file_name+",上传用户："+user_id)
            #将文件存入数据库
            flag=connectsql.read_csv(the_file.filename,china_row_flag,english_row_flag,unit_row_flag,type_flag)#将文件存入数据库、
            #修改状态
            fileroot.file_update_state(file_name,  "已导入数据库")
        #excel_example文件夹xlsx，xls
        elif(file_type=="xlsx" or file_type=="xls"):
            # 保存文件到指定路径
            the_file.save("import_excel/" + the_file.filename)
            file_size=os.path.getsize("import_excel/"+the_file.filename)
            # 记录文件基本信息
            if (flag_came == 0):
                fileroot.file_root(file_name,file_time,file_type,""+hum_convert(file_size),user_id)#记录文件基本信息
                fileroot.file_update_state(file_name,  "已上传")
            print("文件类型：" + file_type + "，文件大小：" +""+hum_convert(file_size)+ ",上传时间：" + file_time + ",文件名：" + file_name+",上传用户："+user_id)
            # 将文件存入数据库
            flag = connectsql.read_example(the_file.filename,china_row_flag,english_row_flag,unit_row_flag,type_flag)
            # 修改状态
            fileroot.file_update_state(file_name,  "已导入数据库")
        #word_data文件夹docx，doc
        elif(file_type=="docx" or file_type=="doc"):
            # 保存文件到指定路径
            the_file.save("import_word/" + the_file.filename)
            file_size=os.path.getsize("import_word/"+the_file.filename)
            # 记录文件基本信息
            fileroot.file_root(file_name,file_time,file_type,""+hum_convert(file_size),user_id)#记录文件基本信息
            fileroot.file_update_state(file_name,  "已上传")
            print("文件类型：" + file_type + "，文件大小：" +""+hum_convert(file_size)+ ",上传时间：" + file_time + ",文件名：" + file_name+",上传用户："+user_id)
        else:
            # 保存文件到指定路径
            the_file.save("import_test/" + the_file.filename)
            file_size=os.path.getsize("import_test/"+the_file.filename)
            # 记录文件基本信息
            fileroot.file_root(file_name,file_time,file_type,""+hum_convert(file_size),user_id)#记录文件基本信息
            fileroot.file_update_state(file_name, "已上传")
            print("文件类型：" + file_type + "，文件大小：" +""+hum_convert(file_size)+ ",上传时间：" + file_time + ",文件名：" + file_name)
            return jsonify({"code": 2, "msg": "", "data": ""})
        if(flag==1):
            print("导入成功")
            if(flag_came==0):
                return jsonify({"code": 1, "msg": "", "data": ""})
            else:
                print("相同文件上传")
                print(fileroot.find_filedata_filename(file_name))
                if (type_0 == "0"):
                    return jsonify({"code": 3, "msg": "", "data": ""})
                else:
                    return jsonify({"code": 4, "msg": "", "data": ""})
        else:
            print("导入失败")
            return jsonify({"code": -1, "msg": "", "data": ""})
#数据导出
@app.route('/export')
def export():
    # 获取表名与数据库名
    table_name = request.values.get("table_name")
    database_name = request.values.get("database_name")
    file_data=fileroot.find_filedata_filename(table_name)[0]
    print("文件下载：")
    if(file_data[2] == "csv" or file_data[2] == "txt"):
        print(file_data)
        return send_from_directory(r"import_csv", filename=file_data[0]+"."+file_data[2], as_attachment=True)
    elif(file_data[2] == "xlsx" or file_data[2] == "xls"):
        print(file_data)
        return send_from_directory(r"import_excel", filename=file_data[0]+"."+file_data[2], as_attachment=True)
    elif(file_data[2] == "docx" or file_data[2] == "doc"):
        print(file_data)
        return send_from_directory(r"import_word", filename=file_data[0] + "." + file_data[2], as_attachment=True)
    else:
        print(file_data)
        return send_from_directory(r"import_test", filename=file_data[0] + "." + file_data[2], as_attachment=True)
#文件自定义列导出
@app.route('/export_select')
def export_select():
    flag=1;
    #获取字符串
    getdata_str = request.values.get("getData_str")
    #获取表名
    table_name=request.values.get("table_name")
    #获取已经导出的excel文件名
    try:
        file_name=connectsql.export_excel(getdata_str,table_name)
    except:
        flag=0
    print("导出文件名:"+file_name)
    return jsonify({"flag":flag,"file_name":file_name})
#自定义文件导出下载：
@app.route("/export_select_download")
def export_select_download():
    file_name = request.values.get("table_name")+".xls"
    return send_from_directory(r"export_excel_select", filename=file_name, as_attachment=True)
######文件导入导出



#######数据查看部分
#获取表列表
@app.route('/get_table_list')
def get_table_list():
    data=[]
    data=dictionary.get_table_data()
    data_re=[]
    for table_name,database_name,rows,data_time in data:
        data_time_str=data_time.strftime("%Y-%m-%d %H:%M:%S")
        data_re.append({"table_name":table_name,"database_name":database_name,"rows_num":rows+1,"create_time":data_time_str})
    count= len(data_re)
    print("已导入数据：")
    print(data_re)
    return jsonify({"code": 0, "msg": "", "count": count,"data":data_re})
#文件状态查询
@app.route('/file_state_list')
def file_state_list():
    file_list=fileroot.file_state_list()
    file_state_list=[]
    count=len(file_list)
    for file_name,file_time,file_type,file_size,file_state,user_id,is_clean in file_list:
        file_state_list.append({"file_name":file_name,"file_time":file_time,"file_type":file_type,"file_size":file_size,"file_state":file_state,"user_id":user_id})
    return jsonify({"code": 0, "msg": "", "count": count, "data": file_state_list})
#查看数据字典
@app.route('/get_look_dictionary')
def get_look_dictionary():
    #获取表名与数据库名
    table_name=request.values.get("table_name")
    database_name=request.values.get("database_name")
    #调用数据字典函数
    table_data=dictionary.get_dictionary(table_name,database_name)
    #返回值
    data_re=[]
    #返回长度
    count=len(table_data)
    #转换为符合规定的JSON格式
    for index in range(len(table_data)):
        data_re.append({"key_english":table_data[index][0],"key_china":table_data[index][1].split(",")[0],"key_type":table_data[index][2],
                        "key_long":table_data[index][3],"key_null":table_data[index][4],"key_unit":table_data[index][1].split(",")[1]})
    print("数据字典：(table_name="+table_name+",database_name="+database_name+")")
    print(data_re)
    return jsonify({"code": 0, "msg": "", "count": count, "data": data_re})
#为了动态展示表的详细信息
#先获取KEY值确定table的表头
#在获取详细值
@app.route('/get_table_details_key')
def get_table_details_key():
    #获取表名与数据库名
    table_name=request.values.get("table_name")
    database_name=request.values.get("database_name")
    english_china=[]
    #调用获取表KEY的函数
    english_china=dictionary.get_table_details_key(table_name,database_name)
    english_china_clean=[]
    for i in english_china:
        english_china_clean.append((i[0],i[1].split(",")[0]))#去掉逗号
    #返回JSON
    print("表key值：(table_name="+table_name+",database_name="+database_name+")")
    print(english_china)
    return jsonify({"data": english_china_clean,"len":len(english_china)})
    pass
@app.route('/get_table_details')
def get_table_details():
    #获取表名与数据库名
    table_name=request.values.get("table_name")
    database_name=request.values.get("database_name")
    # 调用获取表的详细信息
    table_data=dictionary.get_table_details(table_name,database_name)
    english_china=dictionary.get_table_details_key(table_name,database_name)
    #转化为JSON格式
    data_re=[]#最后的形态{"key":value,......}
    flag={}#表的键值
    count=len(table_data)
    for table_data_flag in table_data:
        flag = {}
        for i in range(len(english_china)):
            flag[english_china[i][0]] = table_data_flag[i]#table_data_flag==value,english_china==key
        data_re.append(flag)
    print("表的内容：(table_name="+table_name+",database_name="+database_name+")")
    print(data_re)
    return jsonify({"code": 0, "msg": "", "count": count, "data": data_re})
#获取快速数据分析数据
@app.route("/get_table_clean_key")
def get_table_clean_key():
    # 获取表名与数据库名
    table_name = request.values.get("table_name")
    database_name = request.values.get("database_name")
    #调用获取表KEY的函数
    clean_key_index,clean_index,clean_values= dictionary.get_table_clean(table_name, database_name)
    clean_key=[]
    for i in clean_key_index:
        clean_key.append(i)
    # 返回JSON
    print("返回的clean_key")
    print(clean_key)
    return jsonify({"data": clean_key, "len": len(clean_key)})
    pass
@app.route("/get_table_clean_data")
def get_table_clean_data():
    # 获取表名与数据库名
    table_name = request.values.get("table_name")
    database_name = request.values.get("database_name")
    #调用获取表KEY的函数
    clean_key,clean_index,clean_values= dictionary.get_table_clean(table_name, database_name)
    # 返回JSON
    # 转化为JSON格式
    data_real = []  # 最后的形态{"key":value,......}
    count = len(clean_values)
    for i in range(count):
        flag = {}
        for j in range(len(clean_key)):
            flag[clean_key[j]] = clean_values[i][j]  # table_data_flag==value,english_china==key
        flag["type"]=clean_index[i]
        data_real.append(flag)
    print("数据快速分析内容：(table_name=" + table_name + ",database_name=" + database_name + ")")
    return jsonify({"code": 0, "msg": "", "count": count, "data": data_real})
    pass
#######数据查看部分




######数据字典部分
#根据文件生成数据字典
@app.route("/create_dictionary_file")
def create_dictionary_file():
    flag=0#falg=0表生成失败，flag=1表生成成功，flag=2文件类型不支持，flag=3表已生成
    file_name = request.values.get("file_name")
    file_type = request.values.get("file_type")
    file_data=fileroot.find_filedata_filename(file_name)[0]
    if(file_type=="csv" or file_type=="txt"):
        if(file_data[4]=="已导入数据库"):
            flag=3
        else:
            flag = connectsql.read_csv(file_name+"."+file_type)
            fileroot.file_update_state(file_name, "已导入数据库")
    elif(file_type=="xlsx" or file_type=="xls"):
        if(file_data[4]=="已导入数据库"):
            flag=3
        else:
            flag = connectsql.read_example(file_name+"."+file_type)
            fileroot.file_update_state(file_name, "已导入数据库")
    elif(file_type=="docx" or file_type=="doc"):
        flag=2
    else:
        flag=2
    return jsonify({"flag":flag})
#数据字典修改
@app.route('/update_dictonary')
def update_dictonary():
    table_name = request.values.get("table_name")
    database_name = request.values.get("database_name")
    key_china = request.values.get("key_china")
    key_type = request.values.get("key_type")
    key_english = request.values.get("key_english")
    key_long = request.values.get("key_long")
    key_null = request.values.get("key_null")
    key_unit = request.values.get("key_unit")
    key_english_0 = request.values.get("key_english_0")
    key_unit_0 = request.values.get("key_unit_0")
    flag=dictionary.update_dictionary(table_name,database_name,
        key_china,key_type,key_english,key_long,key_null,key_unit,key_english_0)
    return jsonify({"flag":flag})
#数据字典添加
@app.route('/add_dictonary')
def add_dictonary():
    table_name = request.values.get("table_name")
    database_name = request.values.get("database_name")
    key_china = request.values.get("key_china")
    key_type = request.values.get("key_type")
    key_english = request.values.get("key_english")
    key_long = request.values.get("key_long")
    key_null = request.values.get("key_null")
    key_unit = request.values.get("key_unit")
    flag=dictionary.add_dictionary(table_name,database_name,
        key_china,key_type,key_english,key_long,key_null,key_unit)
    return jsonify({"flag":flag})
#数据字典删除
@app.route('/delete_dictonary')
def delete_dictonary():
    table_name = request.values.get("table_name")
    database_name = request.values.get("database_name")
    key_english = request.values.get("key_english")
    flag=dictionary.delete_dictionary(table_name,database_name,key_english)
    return jsonify({"flag":flag})
######数据字典部分





######表与文件部分
#表删除
@app.route('/delete_table')
def delete_table():
    flag=1
    table_name = request.values.get("table_name")
    database_name = request.values.get("database_name")
    try:
        flag=dictionary.delete_table(table_name)
        fileroot.file_update_state(table_name,"已上传")
    except:
        traceback.print_exc()
        flag=0
    return jsonify({"flag":flag})
#文件删除
@app.route('/delete_file')
def delete_file():
    flag=0;
    file_name = request.values.get("file_name")
    file_type = request.values.get("file_type")
    #获取文件信息，以便获取要删除的文件地址
    #文件删除
    print("文件删除：")
    if (file_type == "csv" or file_type == "txt"):
        print(file_name+file_type)
        os.remove("import_excel/"+file_name+"."+file_type)
        # 文件状态删除
        flag = fileroot.delete_file(file_name)
    elif (file_type == "xlsx" or file_type == "xls"):
        print(file_name+file_type)
        os.remove("import_csv/" + file_name+"."+file_type)
        # 文件状态删除
        flag = fileroot.delete_file(file_name)
    elif (file_type == "docx" or file_type == "doc"):
        print(file_name+file_type)
        os.remove("import_word/" + file_name+"."+file_type)
        # 文件状态删除
        flag = fileroot.delete_file(file_name)
    else:
        print(file_name+file_type)
        os.remove("import_test/" + file_name+"."+file_type)
        # 文件状态删除
        flag = fileroot.delete_file(file_name)
    return jsonify({"flag":flag})
######表与文件部分


#数据可视化
@app.route('/to_look')
def tolook():
    return render_template("tolook.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,debug=True)

