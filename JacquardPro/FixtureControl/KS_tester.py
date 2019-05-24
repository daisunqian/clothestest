# -*- coding=utf-8 -*-

from FixtureControl.KMY_tester_base import *
from FixtureControl.KY_backpack_tester import KMY_backpack_tester


# 背包模组测试
class KS_tester(KMY_backpack_tester):

    def __init__(self, config, limit_config):
        super(KS_tester, self).__init__(config, limit_config)
        self.min_sensor_NO = 0
        self.max_sensor_NO = 12

    # 启动测试
    def start_test(self):
        try:
            self._testing = True
            self.current_test_result = True
            self.start_time = datetime.datetime.now()  # 测试开始时间
            self.current_sn = ''
            test_status = True
            if DEBUG:
                self.test_start.emit()
                for i in range(0, 20):
                    self.item_start.emit("test{0}".format(i))
                    time.sleep(0.5)
                    if i == 20:
                        test_status = False
                        self.item_end.emit("test{0}".format(i), False, str(i), 'Fail')
                    else:
                        self.item_end.emit("test{0}".format(i), True, str(i), 'pass')
                self.current_test_result = test_status
                # self.test_end.emit(self.current_sn, test_status)
            else:
                if self.check_Fixture():
                    # test_exit = self.config_obj.test_exit
                    self._on_test_start()
                    # 1.初始化
                    test_status = self._test_init()
                    check_dut_status = False
                    # 2. 读出dut信息
                    if test_status:
                        check_dut_status = self._check_dut()
                    else:
                        self.current_test_result = False
                    # 3. 采集dut raw count 数据
                    if check_dut_status:
                        test_status = self._check_raw_count()
                        if test_status is False:
                            self.current_test_result = False
                    else:
                        test_status = False
                        self.current_test_result = False

                    # 4. 滚压测试(电机下压，同时检测压力是否在范围内，压力到达门限,停止下压，进行滚动测试)
                    if check_dut_status and self._testing and test_status:
                        test_status = self._roll_test()
                    else:
                        test_status = False
                        self.current_test_result = False

                    if test_status is False:
                        self.current_test_result = False

                    # 5. 振动测试
                    if check_dut_status and self._testing and test_status:
                        test_status = self._vibration_test()
                        if test_status is False:
                            self.current_test_result = False

                    if self.current_test_result:
                        # test_status = self._vibration_test()
                        # 7. 测试结束
                        self._test_finished()
                    else:
                        self.current_test_result = False
                        # 失败复位
                        self._on_display_msg('start_test', 'test fail, start reset', False)
                        self.reset()
                else:
                    self.current_test_result = False

            # self.test_end.emit(self.current_sn, test_status if isinstance(test_status, bool) else False)
            self._on_test_end(self.current_sn, self.current_test_result)
            self.end_time = datetime.datetime.now()  # 测试结束时间
            self._testing = False

            return test_status
        finally:
            self.mcu.stop_collect()

    # 设备回原点
    def backhome(self):
        # 加速度无杆气缸电磁阀上
        status, msg = self._test_finished_step1()

        # 夹紧
        if status:
            status = self._stretch_relax()

        # 下压home
        if status:
            status = self.moon_motor.SetMoonsHome(self.config_obj.Push_down_slave)
        # roll home
        if status:
            self.moon_motor.SetMoonsHome(self.config_obj.Roll_slave)

        # 张紧气缸复位
        if status:
            status, msg = self.__test_finished_step3()

        # 夹紧气缸复位
        if status:
            status, msg = self.__test_finished_step4()

        # 等待结束在继续
        self._wait_moo_stop([self.config_obj.Push_down_slave, self.config_obj.Roll_slave])
        try:
            # 信号等复位
            if status:
                self.kmlio.set_start_lamp(0)
                self.kmlio.set_reset_lamp(1)
                self.kmlio.set_red(0)
                self.kmlio.set_green(0)
                self._buzzer()
            else:
                self.kmlio.set_red(0)
                self._buzzer(5)

            return status
        except Exception, ex:
            self._on_display_msg('reset', 'exception:{0}'.format(str(ex)), False)

    # 复位
    def reset(self):
        # 加速度无杆气缸电磁阀上
        status, msg = self._test_finished_step1()

        # 夹紧
        if status:
            status = self._stretch_relax()

        # 下压电机复位
        if status:
            status = self._Moveline(self.config_obj.Push_down_slave, 0, SPEED)
            self._on_display_msg('reset', 'down press motor reset {0}'.format('OK' if status else 'fail'), status)

        # 滚动电机复位
        if status:
            status = self._Moveline(self.config_obj.Roll_slave, 0, SPEED)
            self._on_display_msg('reset', 'roll motor reset {0}'.format('OK' if status else 'fail'), status)

        # 张紧气缸复位
        if status:
            status, msg = self.__test_finished_step3()

        # 夹紧气缸复位
        if status:
            status, msg = self.__test_finished_step4()

        # 等待结束在继续
        self._wait_moo_stop([self.config_obj.Push_down_slave, self.config_obj.Roll_slave])
        try:
            # 信号等复位
            if status:
                self.kmlio.set_start_lamp(0)
                self.kmlio.set_reset_lamp(1)
                self.kmlio.set_red(0)
                self.kmlio.set_green(0)
                self._buzzer()
            else:
                self.kmlio.set_red(0)
                self._buzzer(5)

            return status
        except Exception, ex:
            self._on_display_msg('reset', 'exception:{0}'.format(str(ex)), False)


    # 张紧气缸释放
    def __test_finished_step3(self):
        try:
            test_status = True
            msg = '__test_finished_step3 ok'
            status, set_data = self.kmlio.set_stretch_tensioning(1)
            if status is True:
                value, data = self.kmlio.get_stretch_relax(1, True)  # 张紧气缸放松
                if value != 1:
                    test_status = False
                    msg = 'get_stretch_relax  fail value={0}, data={1}'.format(value, data)
            else:
                test_status = False
                msg = 'set_stretch_tensioning fail'

            return test_status, msg
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status, msg
        finally:
            self._on_display_msg('__test_finished_step3', msg, test_status)

    # 夹爪气缸释放
    def __test_finished_step4(self):
        try:
            test_status = True
            msg = '__test_finished_step4 ok'
            status, set_data = self.kmlio.set_stretch_relax(1)
            if status is True:
                value, data = self.kmlio.get_claw_loosen(0, True)
                if value != 1:
                    test_status = False
                    msg = 'get_claw_loosen  fail, value={0}, data={1}'.format(value, data)
            else:
                test_status = False
                msg = 'set_stretch_relax 0 fail'

            return test_status, msg
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status, msg
        finally:
            self._on_display_msg('__test_finished_step4', msg, test_status)