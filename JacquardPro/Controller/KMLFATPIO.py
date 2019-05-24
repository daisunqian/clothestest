# -*- coding=utf-8 -*-

from Controller.IOControl import IOControl


IN1 = 1    # E-Stop 急停按钮
IN2 = 2    # start button启动按钮1
IN3 = 3    # start button启动按钮2
IN4 = 4    # reset button复位按钮
IN5 = 5    # 加速度无杆气缸上位
IN6 = 6    # 加速度无杆气缸下位
IN7 = 7    # 张紧气缸拉紧
IN8 = 8    # 张紧气缸放松
IN9 = 9    # 夹爪气缸夹紧
IN10 = 10  # 夹爪气缸松开
IN11 = 11  # 滚压驱动器报警
IN12 = 12  # loadcell下压驱动器报警
IN13 = 13  # 真空检测
IN14 = 14  # 安全光栅
IN15 = 15  # 脚踏开关
IN16 = 16  # 产品检测光电开关

OUT1 = 1    # 启动指示灯
OUT2 = 2    # 复位指示灯
OUT3 = 3    # 三色灯(绿）
OUT4 = 4    # 三色灯(红）
OUT5 = 5    # 三色灯(蓝）
OUT6 = 6    # 三色灯(蜂鸣器）
OUT7 = 7    # 加速度无杆气缸电磁阀上
OUT8 = 8    # 加速度无杆气缸电磁阀下
OUT9 = 9    # 张紧气缸
OUT10 = 10  # 夹爪气缸
OUT11 = 11  # 真空阀开关
OUT12 = 12  # 压力表数据清除

# 输入IO设备初始化状态判定值
INPUT_IO_LIMIT = [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0]


# 半成品io
class KMLFATPIO(IOControl):
    def __init__(self,  port, baudrate=115200):
        super(KMLFATPIO, self).__init__(port, baudrate)

    # E-Stop 急停按钮
    # 返回：1=按下，0=未按下
    def get_E_Stop(self):
        return self.get_input(IN1)

    # start button启动按钮1
    # tovalue 是需要读到这个，tovalue=1
    # wait true循环读，直到到value的值返回
    # timeout 超时时间,单位秒（默认10秒）
    # 返回：1=按下，0=未按下
    def get_start_button1(self, tovalue=1, wait=False, timeout=10):
        rtn = self._read_input(IN2, tovalue, wait, timeout)
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]
        # return self._read_input(IN2, tovalue, wait, timeout)

    # start button启动按钮2
    # tovalue 是需要读到这个，tovalue=1
    # wait true循环读，直到到value的值返回
    # timeout 超时时间,单位秒（默认10秒）
    # 返回：1=按下，0=未按下
    def get_start_button2(self, tovalue=1, wait=False, timeout=10):
        rtn = self._read_input(IN3, tovalue, wait, timeout)
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]
        # return self._read_input(IN3, tovalue, wait, timeout)

    # reset button复位按钮
    # 返回：1=按下，0=未按下
    def get_reset_button(self):
        rtn = self._read_input(IN4)
        if rtn[0] == 1:
            return 0, rtn[1]
        else:
            return 1, rtn[1]

    # 加速度无杆气缸上位
    # 返回：1=上位，0=不在上位
    def get_accelerated_up(self, tovalue=1, wait=False, timeout=10):
        rtn = self._read_input(IN5, tovalue, wait, timeout)
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]
        # return self._read_input(IN5, tovalue, wait, timeout)

    # 加速度无杆气缸下位
    # 返回：1=下位，0=不在下位
    def get_accelerated_down(self, tovalue=1, wait=False, timeout=10):
        # tovalue = 0 if tovalue == 1 else 1
        rtn = self._read_input(IN6, tovalue, wait, timeout)
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]
        # return self._read_input(IN6, tovalue, wait, timeout)

    # 张紧气缸拉紧
    # 返回：1=拉紧，0=未拉紧
    def get_stretch_tensioning(self, tovalue=1, wait=False, timeout=10):
        return self._read_input(IN7, tovalue, wait, timeout)

    # 张紧气缸放松
    # 返回：1=放松，0=未放松
    def get_stretch_relax(self, tovalue=1, wait=False, timeout=10):
        return self._read_input(IN8, tovalue, wait, timeout)

    # 夹爪气缸夹紧
    # 返回：1=夹紧，0=未夹紧
    def get_claw_clamp(self, tovalue=1, wait=False, timeout=10):
        rtn = self._read_input(IN9, tovalue, wait, timeout)
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]

    # 夹爪气缸松开
    # 返回：1=松开，0=未松开
    def get_claw_loosen(self, tovalue=1, wait=False, timeout=10):
        # rtn = self._read_input(IN10, tovalue, wait, timeout)
        # return rtn
        rtn = self._read_input(IN10, tovalue, wait, timeout)
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]

    # 滚压驱动器报警
    # 返回：1=报警，0=未报警
    def get_roll_warning(self):
        rtn = self._read_input(IN11)    # io 返回0是有报警,否则没有
        print rtn, 'get_roll_warning'
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]
        # return self._read_input(IN11)

    # loadcell下压驱动器报警
    # 返回:1=报警，0=未报警
    def get_loadcell_warning(self):
        rtn = self._read_input(IN12)  # io 返回0是有报警,否则没有
        print rtn, 'get_loadcell_warning'
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]
        # return self._read_input(IN12)

    # 真空检测
    # 返回：1=真空状态,0=不在真空状态
    def get_vacuo(self, tovalue=1, wait=False, timeout=10):
        return self._read_input(IN13, tovalue, wait, timeout)

    # 安全光栅
    # 返回：1=发生遮挡，0=正常
    def get_safty_raster(self):
        return self._read_input(IN14)

    # 脚踏开关
    # 返回：1=脚踏关(踩下),0=脚踏开(释放)
    def get_foot_switch(self, tovalue=1, wait=False, timeout=10):
        rtn = self._read_input(IN15, tovalue, wait, timeout)
        if rtn[0] == 0:
            return 1, rtn[1]
        else:
            return 0, rtn[1]

    # 产品检测光电开关
    def get_product_checked(self, tovalue=1, wait=False, timeout=10):
        return self._read_input(IN16, tovalue, wait, timeout)

    # 启动指示灯
    # on_off=1开，on_off=0关
    def set_start_lamp(self, on_off):
        return self.write_output(OUT1, on_off)

    # 复位指示灯
    # on_off=0开，on_off=1关
    def set_reset_lamp(self, on_off):
        return self.write_output(OUT2, on_off)

    # 三色灯(绿）
    # on_off=0开，on_off=1关
    def set_green(self, on_off):
        return self.write_output(OUT3, on_off)

    # 三色灯(红）
    # on_off=0开，on_off=1关
    def set_red(self, on_off):
        return self.write_output(OUT4, on_off)

    # 三色灯(蓝）
    # on_off=0开，on_off=1关
    def set_blue(self, on_off):
        return self.write_output(OUT5, on_off)

    # 蜂鸣器
    # on_off=0开，on_off=1关
    def set_buzzer(self, on_off):
        return self.write_output(OUT6, on_off)

    # 加速度无杆气缸电磁阀下
    # on_off=0开，on_off=1关
    def set_accelerated_down(self, on_off):
        self.write_output(OUT7, on_off==False)
        return self.write_output(OUT8, on_off)

    # 加速度无杆气缸电磁阀上
    # on_off=0开，on_off=1关
    def set_accelerated_up(self, on_off):
        self.write_output(OUT8, on_off==False)
        return self.write_output(OUT7, on_off)

    # 张紧气缸
    # on_off=0开，on_off=1关
    def set_stretch_tensioning(self, on_off):
        return self.write_output(OUT9, on_off)

    # 夹爪气缸
    # on_off=0开，on_off=1关
    def set_stretch_relax(self, on_off):
        return self.write_output(OUT10, on_off)

    # 真空阀开关
    # on_off=0开，on_off=1关
    def set_vacuum_switch(self, on_off):
        return self.write_output(OUT11, on_off)

    # loadcell压力表数据清除
    # on_off=0开，on_off=1关
    def set_loadcell_clear(self, on_off):
        return self.write_output(OUT12, on_off)


if __name__ == '__main__':
    innorev = KMLFATPIO("COM4")
    # print innorev.get_E_Stop()
    # print innorev.get_start_button1()
    # print innorev.get_accelerated_up()
    # print innorev.get_accelerated_down()
    # print innorev.get_stretch_tensioning()
    # print innorev.get_stretch_relax()
    print innorev.get_claw_clamp()
    # print innorev.get_claw_loosen()