# -*- coding=utf-8 -*-


from Produce.KML_garment_Produce import KML_garment_Produce


# 创建对象
def creat_produce(type, appconfig):
    if type == 1:
        return KML_garment_Produce(appconfig)
    else:
        return None