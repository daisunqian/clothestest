# -*-coding=utf-8 -*-


from ConfigParser import ConfigParser

TEST_TYPE_Names = [u"成品衣服测试", u'半成品衣服测试',
                   u'KY背包测试', u'KS背包测试',u'IQC测试']
TEST_TYPE_KEYS = ["KML_Garment_tester", 'KML_Cuff_tester',
                  'KMY_Backpack_tester','KS_tester','IQC_tester']

TEST_TYPE = dict(zip(TEST_TYPE_KEYS, TEST_TYPE_Names))


# 应用配置文件读取和写入
class APPConfigparse(object):
    def __init__(self, path):
        self.path = path
        self.config = ConfigParser()
        # self.fp_limit = open(path, "r")
        # self.config.readfp(self.fp_limit)
        self.config.read(self.path)

    # 保存数据
    def _save_value(self):
        # print self.path
        with open(self.path, "w+") as f:
            self.config.write(f)
        self.config.read(self.path)    # 从读数据

    # true是调试模式
    @property
    def Debug(self):
        try:
            return self.config.getboolean('Application', 'debug')
        except Exception, ex:
            self.config.set('Application', 'debug', False)

    # true是调试模式
    @Debug.setter
    def Debug(self, debug):
        self.config.set('Application', 'debug', debug)
        self._save_value()

    # 测试模式：1=滚动测试模式，2=矩形面压模式
    @property
    def Test_mode(self):
        try:
            return self.config.getboolean('Application', 'test_mode')
        except Exception, ex:
            self.config.set('Application', 'test_mode', 1)

    # 同产品通讯类型，1=使用mcu通讯，2=使用客户通讯设备通讯
    @property
    def mcu_type(self):
        try:
            return self.config.getint('Application', 'mcu_type')
        except Exception, ex:
            self.config.set('Application', 'mcu_type', 1)

    # true 某一步测试失败将退出测试复位，否则继续测试
    @property
    def test_exit(self):
        try:
            return self.config.getboolean('Application', 'test_exit')
        except Exception, ex:
            self.config.set('Application', 'test_exit', True)

    # 当前登录用户名
    @property
    def UserName(self):
        try:
            return self.config.get('Application', 'uname')
        except Exception, ex:
            self.config.set('Application', 'uname', '')

    # 登录密码
    @property
    def Login_pwd(self):
        try:
            return self.config.get('Application', 'login_pwd')
        except Exception, ex:
            self.config.set('Application', 'login_pwd', '6f88a95d47de53c5defbbb18205ac244')

    # 参数修改密码密码
    @property
    def Update_pwd(self):
        try:
            return self.config.get('Application', 'update_pwd')
        except Exception, ex:
            self.config.set('Application', 'update_pwd', 'dcfa72075c794f5ced531f27f18ac36d')

    # 当前登录用户名
    @UserName.setter
    def UserName(self, name):
        self.config.set('Application', 'uname', name)
        self._save_value()

    # 测试类型(详细说明见'说明.txt'文件)
    @property
    def Test_type(self):
        try:
            return self.config.get('Application', 'test_type')
        except Exception, ex:
            self.config.set('Application', 'test_type', '')

    # io 通讯端口
    @property
    def IO_Port(self):
        try:
            return self.config.get('Coumucation', 'io_port')
        except Exception, ex:
            self.config.set('Coumucation', 'io_port', '')

    # io 通讯端口
    @IO_Port.setter
    def IO_Port(self, port):
        self.config.set('Coumucation', 'io_port', port)
        self._save_value()

    # io 通讯波特率
    @property
    def IO_baudrate(self):
        try:
            return self.config.getint('Coumucation', 'io_baudrate')
        except Exception, ex:
            self.config.set('Coumucation', 'io_baudrate', 115200)

    # io 通讯波特率
    @IO_baudrate.setter
    def IO_baudrate(self, baudrate):
        self.config.set('Coumucation', 'io_baudrate', baudrate)
        self._save_value()

    # loadcell 通讯端口
    @property
    def loadcell_port(self):
        try:
            return self.config.get('Coumucation', 'loadcell_port')
        except Exception, ex:
            self.config.set('Coumucation', 'loadcell_port', '')

    # loadcell 通讯端口
    @loadcell_port.setter
    def loadcell_port(self, port):
        self.config.set('Coumucation', 'loadcell_port', port)
        self._save_value()

    # loadcell 通讯波特率
    @property
    def loadcell_braudate(self):
        try:
            return self.config.getint('Coumucation', 'loadcell_braudate')
        except Exception, ex:
            self.config.set('Coumucation', 'loadcell_braudate', 19200)

    # loadcell 通讯波特率
    @loadcell_braudate.setter
    def loadcell_braudate(self, baudrate):
        self.config.set('Coumucation', 'loadcell_braudate', baudrate)
        self._save_value()

    # 振动测试 通讯端口
    @property
    def Acc_port(self):
        try:
            return self.config.get('Coumucation', 'acc_port')
        except Exception, ex:
            self.config.set('Coumucation', 'acc_port', '')

    # 振动测试 通讯端口
    @Acc_port.setter
    def Acc_port(self, port):
        self.config.set('Coumucation', 'acc_port', port)
        self._save_value()

    # 振动测试 通讯波特率
    @property
    def Acc_braudate(self):
        try:
            return self.config.getint('Coumucation', 'acc_braudate')
        except Exception, ex:
            self.config.set('Coumucation', 'acc_braudate', 19200)

    # 振动测试 通讯波特率
    @Acc_braudate.setter
    def Acc_braudate(self, baudrate):
        self.config.set('Coumucation', 'acc_braudate', baudrate)
        self._save_value()

    # mcu测试 通讯端口
    @property
    def MCU_Port(self):
        try:
            return self.config.get('Coumucation', 'mcu_port')
        except Exception, ex:
            self.config.set('Coumucation', 'mcu_port', '')

    # mcu测试 通讯端口
    @MCU_Port.setter
    def MCU_Port(self, port):
        self.config.set('Coumucation', 'mcu_port', port)
        self._save_value()

    # mcu测试 通讯波特率
    @property
    def MCU_braudate(self):
        try:
            return self.config.getint('Coumucation', 'mcu_braudate')
        except Exception, ex:
            self.config.set('Coumucation', 'mcu_braudate', 19200)

    # mcu测试 通讯波特率
    @MCU_braudate.setter
    def MCU_braudate(self, baudrate):
        self.config.set('Coumucation', 'mcu_braudate', baudrate)
        self._save_value()

    # 电机测试 通讯端口
    @property
    def Moon_motor_Port(self):
        try:
            return self.config.get('Coumucation', 'moon_motor_port')
        except Exception, ex:
            self.config.set('Coumucation', 'moon_motor_port', '')

    # 电机测试 通讯端口
    @Moon_motor_Port.setter
    def Moon_motor_Port(self, port):
        self.config.set('Coumucation', 'moon_motor_port', port)
        self._save_value()

    # 电机测试 通讯波特率
    @property
    def Moon_motor_braudate(self):
        try:
            return self.config.getint('Coumucation', 'moon_motor_braudate')
        except Exception, ex:
            self.config.set('Coumucation', 'moon_motor_braudate', 19200)

    # 电机测试 通讯波特率
    @Moon_motor_braudate.setter
    def Moon_motor_braudate(self, baudrate):
        self.config.set('Coumucation', 'moon_motor_braudate', baudrate)
        self._save_value()


    # 下压电机从地址
    @property
    def Push_down_subordinate(self):
        try:
            return self.config.getint('Motion', 'push_down_subordinate')
        except Exception, ex:
            self.config.set('Motion', 'push_down_subordinate', 1)

    # 下压运动目标距离1，到位后一定不能接触到dut,并且比Roll_pressure_pos小
    @property
    def Pressure_target_pos(self):
        try:
            return self.config.getint('Motion', 'pressure_target_pos')
        except Exception, ex:
            self.config.set('Motion', 'pressure_target_pos', 1)

    # 下压运动目标距离1，到位后一定不能接触到dut,并且比Roll_pressure_pos小
    @Pressure_target_pos.setter
    def Pressure_target_pos(self, pos):
        self.config.set('Motion', 'pressure_target_pos', pos)
        self._save_value()

    # 垂直滚动下压运动距离
    @property
    def Roll_pressure_pos(self):
        try:
            return self.config.getint('Motion', 'roll_pressure_pos')
        except Exception, ex:
            self.config.set('Motion', 'roll_pressure_pos', 1)

    # 垂直滚动下压运动距离
    @Roll_pressure_pos.setter
    def Roll_pressure_pos(self, pos):
        self.config.set('Motion', 'Roll_pressure_pos', pos)
        self._save_value()

    # 滚动电机地址
    @property
    def Roll_subordinate(self):
        try:
            return self.config.getint('Motion', 'roll_subordinate')
        except Exception, ex:
            self.config.set('Motion', 'roll_subordinate', 2)

    # 滚动运动距离
    @property
    def Roll_pos(self):
        try:
            return self.config.getint('Motion', 'roll_pos')
        except Exception, ex:
            self.config.set('Motion', 'roll_pos', 1)

    # 滚动测试起始位置
    @property
    def Roll_start_pos(self):
        try:
            return self.config.getint('Motion', 'roll_start_pos')
        except Exception, ex:
            self.config.set('Motion', 'roll_start_pos', 1)

    # 振动器位置
    @property
    def Vibrator_pos(self):
        try:
            return self.config.getint('Motion', 'vibrator_pos')
        except Exception, ex:
            self.config.set('Motion', 'vibrator_pos', 1)

    # 接触最大压力值
    @property
    def MaxN(self):
        try:
            return self.config.getfloat('Limit', 'MaxN')
        except Exception, ex:
            self.config.set('Limit', 'MaxN', 1)

    # 生成测试文件存储目录
    @property
    def Produce_dir(self):
        try:
            return self.config.get('LOG', 'produce_dir')
        except Exception, ex:
            self.config.set('LOG', 'produce_dir', '.\\produce_summary')

    # 日志文件存储路径
    # 默认是当前程序执行路径
    @property
    def App_log_dir(self):
        try:
            return self.config.get('LOG', 'app_log_dir')
        except Exception, ex:
            self.config.set('LOG', 'app_log_dir', '.\\')

    # 产品测试文件存储路径
    # 默认是当前程序执行路径\summary
    @property
    def Summary_dir(self):
        try:
            return self.config.get('LOG', 'summary_dir')
        except Exception, ex:
            self.config.set('LOG', 'summary_dir', '.\\summary')

  # 感应器的条数
    @property
    def min_sensor_NO(self):
        try:
            return self.config.getint('Application', 'min_sensor_NO')
        except Exception, ex:
            self.config.set('Application', 'min_sensor_NO', 1)

# 感应器的条数
    @property
    def max_sensor_NO(self):
        try:
            return self.config.getint('Application', 'max_sensor_NO')
        except Exception, ex:
            self.config.set('Application', 'max_sensor_NO', 11)

    @property
    def wait_time_out(self):
        try:
            return self.config.getint('Application', 'wait_time_out')
        except Exception, ex:
            self.config.set('Application', 'wait_time_out', 10)


if __name__ == "__main__":
    appconfig = APPConfigparse(r'../config.ini')
    # print appconfig.Pressure_target_pos
    # appconfig.Pressure_target_pos = 280000
    # print appconfig.Pressure_target_pos
    print appconfig.Debug
    print appconfig.Roll_start_pos
    print appconfig.mcu_type
    print appconfig.test_exit
    print appconfig.max_sensor_NO
    print appconfig.wait_time_out