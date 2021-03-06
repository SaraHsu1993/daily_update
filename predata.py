# import codecs
# import os
# os.chdir(os.path.abspath('/Users/path'))
import pandas as pd
from sshtunnel import SSHTunnelForwarder
import pymysql

server = SSHTunnelForwarder(
    'xxx.xx.xxx.xx',
    ssh_username='xxxxxx',
    ssh_password='xxxxxx',
    remote_bind_address=('127.0.0.1', 3306)
)
server.start()

# 更新数据库
# 动态连接&识别新增数据并更新数据库（还没做）
conn = pymysql.connect(
    host='127.0.0.1',
    port=server.local_bind_port,
    user='root',
    password='xxxxxx',
    db='xxxxxx'
)
cur = conn.cursor()

# connect database, get data as .txt file then parse it to .csv file
# df = pd.DataFrame([],columns = ["taxPersonCode","companyName","unifiedCreditCodeZero","unifiedCreditCodeNotZero"])
# file = codecs.open('origindata.txt','r',encoding='utf8')
# lines = file.readlines()
# for line in lines:
#     element = line.split("|")
#     df.loc[len(df)] = {"taxPersonCode": element[1].strip(), "companyName": element[2].strip(), "unifiedCreditCodeZero": element[3].strip(),"unifiedCreditCodeNotZero":element[4].strip()}
# # df.to_csv("ori1.csv")

df = pd.read_csv('/Users/path/ori2.csv')

import re
import CheckCode
df["pretaxPersonCode"] = ''
for i in range(len(df)):
    df.loc[i, "taxPersonCode"] = df.loc[i]["taxPersonCode"].upper()
    print(i)
    # 号码由双括号扩起，第一位为"("
    if df.loc[i]["taxPersonCode"][0] == "(":
        df.loc[i, "pretaxPersonCode"] = re.findall('\((.*?)\)', df.loc[i]["taxPersonCode"])
        str_pretaxPersonCode = ''.join(str(e) for e in df.loc[i]["pretaxPersonCode"])

        # 如果是15位，应该可以直接加91，再作两种运算
        if len(str_pretaxPersonCode) == 15:
            df.loc[i, "unifiedCreditCodeZero"] = CheckCode.Test().CheckCode(str_pretaxPersonCode, 2)
            df.loc[i, "unifiedCreditCodeNotZero"] = CheckCode.Test().CheckCode(str_pretaxPersonCode, 1)

        # 如果是18位，先判断前两位是否是91，是则取3-17位作两种计算（还可以与第18位进行比较验算）
        elif len(str_pretaxPersonCode) == 18:
            if str_pretaxPersonCode[0:2] == '91':
                df.loc[i, "unifiedCreditCodeZero"] = CheckCode.Test().CheckCode(str_pretaxPersonCode[2:17], 2)
                df.loc[i, "unifiedCreditCodeNotZero"] = CheckCode.Test().CheckCode(str_pretaxPersonCode[2:17], 1)
                # check str_pretaxPersonCode[17] == CheckCode.Test().CheckCode(str_pretaxPersonCode[2:17], 1 or 2) or not
            else:
                df.loc[i, "unifiedCreditCodeZero"] = "NULL"
                df.loc[i, "unifiedCreditCodeNotZero"] = "NULL"

        # 如果是16位，取1-15位作两种计算（还可以与第16位进行比较）
        elif len(str_pretaxPersonCode) == 16:
            df.loc[i, "unifiedCreditCodeZero"] = CheckCode.Test().CheckCode(str_pretaxPersonCode[0:15], 2)
            df.loc[i, "unifiedCreditCodeNotZero"] = CheckCode.Test().CheckCode(str_pretaxPersonCode[0:15], 1)
            # check str_pretaxPersonCode[15] == CheckCode.Test().CheckCode(str_pretaxPersonCode[0:15], 1 or 2) or not

    # 号码没有括号扩起，第一位为数字
    elif df.loc[i]["taxPersonCode"][0] != "(":
        str_taxPersonCode = ''.join(str(e) for e in df.loc[i]["taxPersonCode"])
        # 如果是15位，应该可以直接加91，再作两种运算
        if len(str_taxPersonCode) == 15:
            df.loc[i, "unifiedCreditCodeZero"] = CheckCode.Test().CheckCode(str_taxPersonCode, 2)
            df.loc[i, "unifiedCreditCodeNotZero"] = CheckCode.Test().CheckCode(str_taxPersonCode, 1)

        # 如果是16位，取1-15位作两种计算（还可以与第16位进行比较）
        elif len(str_taxPersonCode) == 16:
            df.loc[i, "unifiedCreditCodeZero"] = CheckCode.Test().CheckCode(str_taxPersonCode[0:15], 2)
            df.loc[i, "unifiedCreditCodeNotZero"] = CheckCode.Test().CheckCode(str_taxPersonCode[0:15], 1)
        # check str_taxPersonCode[15] == CheckCode.Test().CheckCode(str_taxPersonCode[0:15], 1 or 2) or not

        # 出现17位的数，以14开头，应该是错误数据，保留Null
        elif len(str_taxPersonCode) == 17:
            df.loc[i, "unifiedCreditCodeZero"] = "NULL"
            df.loc[i, "unifiedCreditCodeNotZero"] = "NULL"

        # 出现19位的数，以14开头，应该是错误数据，保留Null
        elif len(str_taxPersonCode) == 19:
            df.loc[i, "unifiedCreditCodeZero"] = "NULL"
            df.loc[i, "unifiedCreditCodeNotZero"] = "NULL"

        # 出现18位的数，先判断前两位是否是91，是则取3-17位作两种计算（还可以与第18位进行比较验算）
        elif len(str_taxPersonCode) == 18:
            if str_taxPersonCode[0:2] == '91':
                df.loc[i, "unifiedCreditCodeZero"] = CheckCode.Test().CheckCode(str_taxPersonCode[2:17], 2)
                df.loc[i, "unifiedCreditCodeNotZero"] = CheckCode.Test().CheckCode(str_taxPersonCode[2:17], 1)
                # check str_taxPersonCode[17] == CheckCode.Test().CheckCode(str_taxPersonCode[2:17], 1 or 2) or not
            else:
                df.loc[i, "unifiedCreditCodeZero"] = "NULL"
                df.loc[i, "unifiedCreditCodeNotZero"] = "NULL"

        # 出现30位的数，格式为"前18位(11位)"，括号前的78位为00，括号后的78位为区县级
        elif len(str_taxPersonCode) == 30:
            if str_taxPersonCode[0:2] == '91':
                # 1-17位计算市级校验位（还可以与第18位进行比较验算），20-30位替换3-13位计算区县级校验位
                df.loc[i, "unifiedCreditCodeZero"] = CheckCode.Test().CheckCode(str_taxPersonCode[2:17], 2)
                # check str_taxPersonCode[17] == CheckCode.Test().CheckCode(str_taxPersonCode[2:17], 1 or 2) or not

                # 20-30位替换3-13位计算区县级校验位，1-17位计算校验位（还可以与第18位进行比较验算）
                liststr_taxPC = list(str_taxPersonCode)
                liststr_taxPC[2:13] = liststr_taxPC[19:30]
                joinliststr_taxPC = "".join(liststr_taxPC)
                df.loc[i, "unifiedCreditCodeNotZero"] = CheckCode.Test().CheckCode(joinliststr_taxPC[2:17], 1)
                # check str_taxPersonCode[17] == CheckCode.Test().CheckCode(joinliststr_taxPC[2:17], 1 or 2) or not
            else:
                df.loc[i, "unifiedCreditCodeZero"] = "NULL"
                df.loc[i, "unifiedCreditCodeNotZero"] = "NULL"

    else:
        df.loc[i, "unifiedCreditCodeZero"] = "NULL"
        df.loc[i, "unifiedCreditCodeNotZero"] = "NULL"

    # update database
    testsql = """UPDATE TaxationCode SET unifiedCreditCodeNotZero = %s, unifiedCreditCodeZero = %s WHERE taxPersonCode = %s"""
    data = ((df.loc[i]["unifiedCreditCodeNotZero"]), (df.loc[i]["unifiedCreditCodeZero"]), (df.loc[i]["taxPersonCode"]))
    cur.execute(testsql, data)
    conn.commit()

    print(i)

df1 = df[['taxPersonCode','companyName','unifiedCreditCodeZero','unifiedCreditCodeNotZero']]
df1.to_csv("/Users/path/result3.csv", index = False, header = False)

cur.close()
# 关闭数据库连接
conn.close()
# Make sure to call server.stop() when you want to disconnect
server.stop()
