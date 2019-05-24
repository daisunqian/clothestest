# -*- coding:utf-8 -*-


import numpy as np
import pandas
import math

def module():
    df = pandas.read_csv(r'C:\Users\hely\Desktop\acc\acc20190310_module4.csv')

    columns = ["X加速度","Y加速度","Z加速度","X角速度","Y角速度","Z角速度","X角度","Y角度", "Z角度"]
    # 振动前
    pro_df = df[0:6]
    pro_fc_ls = []
    for cln in columns:
        datas = pro_df[cln]
        pro_fc_ls.append(round(np.std(datas, ddof=1), 4))
    print 'pro_fc_ls', pro_fc_ls

    # 振动
    acc_df = df[6:63]
    acc_ls = []
    for cln in columns:
        datas = acc_df[cln]
        acc_ls.append(round(np.std(datas, ddof=1), 4))
    print 'acc_ls', acc_ls

    # 振动后
    ang_df = df[63:69]
    # print ang_df
    ang_ls = []
    for cln in columns:
        datas = ang_df[cln]
        ang_ls.append(round(np.std(datas, ddof=1), 4))
    print 'ang_ls', ang_ls


if __name__ == "__main__":
    module()