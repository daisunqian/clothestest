# -*-coding=utf-8 -*-

from FixtureControl.KML_garment_tester import KML_garment_tester
from FixtureControl.KS_tester import KS_tester
from FixtureControl.KY_backpack_tester import KMY_backpack_tester
from FixtureControl.Limit import LimitConfig
from FixtureControl.IQC import IQC_tester


class JacpuardTestFactory(object):
    def __init__(self):
        pass

    # 创建测试对象
    #参数(test_type测试类型， config配置文件对象)
    @staticmethod
    def create_JacpuardTest(test_type, config, limit_config):

        if test_type == 'KML_Cuff_tester':
            # 衣服半成品测试
            return KML_garment_tester(config, limit_config)
        elif test_type == 'KML_Garment_tester':
            # 衣服成品测试
            return KML_garment_tester(config, limit_config)
        elif test_type == 'KS_tester':
            # KS背包测试
            return KS_tester(config, limit_config)
        elif test_type == 'KMY_Strap_tester':
            # 背包半成品测试
            return KMY_backpack_tester(config, limit_config)
        elif test_type == 'KMY_Backpack_tester':
            # 背包成品测试
            return KMY_backpack_tester(config, limit_config)

        elif test_type == 'IQC_tester':
            # 背包成品测试
            return IQC_tester(config, limit_config)


if __name__ == "__main__":
    from FixtureControl.APPConfigparse import APPConfigparse
    appconfig = APPConfigparse(r'../config.ini')
    limit_config = LimitConfig(r'../limit.ini')
    obj = JacpuardTestFactory.create_JacpuardTest(appconfig.Test_type, appconfig, limit_config)
    print obj
    # obj.check_connect()