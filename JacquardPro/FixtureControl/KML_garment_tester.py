# -*- coding=utf-8 -*-

from FixtureControl.KML_tester_base import *


# 衣服测试
class KML_garment_tester(KML_tester_base):

    def __init__(self, config, limit_config):
        super(KML_garment_tester, self).__init__(config, limit_config)

    # 设备回原点
    def backhome(self):
        # 加速度无杆气缸电磁阀上
        status, msg = self._test_finished_step1()
        # 下压home
        if status:
            status = self.moon_motor.SetMoonsHome(self.config_obj.Push_down_subordinate)
        # roll home
        if status:
            if self.moon_motor.CheckHomeStatus(self.config_obj.Push_down_subordinate):
                self.moon_motor.SetMoonsHome(self.config_obj.Roll_subordinate)

        # 张紧气缸复位
        if status:
            status, msg = self.__test_finished_step3()

        # 夹紧气缸复位
        if status:
            status, msg = self.__test_finished_step4()

        # 等待结束在继续
        self._wait_moo_stop([self.config_obj.Push_down_subordinate, self.config_obj.Roll_subordinate])
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
        self.current_test_result = False
        # 加速度无杆气缸电磁阀上
        status, msg = self._test_finished_step1()

        # 下压电机复位
        if status:
            status = self._Moveline(self.config_obj.Push_down_subordinate, 0, SPEED, False)
            self._on_display_msg('reset', 'down press motor reset {0}'.format('OK' if status else 'fail'), status)

        # 滚动电机复位
        if status:
            if self.moon_motor.CheckHomeStatus(self.config_obj.Push_down_subordinate):
                status = self._Moveline(self.config_obj.Roll_subordinate, 0, SPEED, False)
                self._on_display_msg('reset', 'roll motor reset {0}'.format('OK' if status else 'fail'), status)
            else:
                status = False

        # 张紧气缸复位
        if status:
            status, msg = self.__test_finished_step3()

        # 夹紧气缸复位
        if status:
            status, msg = self.__test_finished_step4()

        # 等待结束在继续
        self._wait_moo_stop([self.config_obj.Push_down_subordinate, self.config_obj.Roll_subordinate])
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

    # 测试初始化
    def _test_init(self):
        try:
            self.current_item = 'test_init'
            self._on_item_start(self.current_item)
            # 夹紧
            msg = '_test_init ok'
            test_status = self._stretch_relax()
            # 4. 张紧
            if test_status:
                test_status = self._stretch_tensioning()
                if test_status is False:
                    msg = '_stretch_tensioning fail'
            else:
                msg = '_stretch_relax fail'
            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:' + ex.message
            return test_status
        finally:
            self._on_item_end(self.current_item, test_status, msg, msg)
            self._on_display_msg('_test_init', msg, test_status)

    # 滚动测试
    def _roll_test(self, dut=True):
        test_status = False
        # 加速度无杆气缸电磁阀上状态检测
        test_status, msg = self._check_accelerated_up()

        # 1. 运动到下压起始位置(测试位置)
        if test_status and self._testing:
            test_status = self.__roll_test_step1()

        # 2.下压电机运动以及找到接触点
        if test_status and self._testing:
            test_status = self.__roll_test_step2()

        if dut is False:
            subordinate = self.config_obj.Roll_subordinate
            pos = self.config_obj.Roll_pos
            test_status = self._Moveline(subordinate, pos, ROLL_SPEED)
            return test_status

        # # 3开启t命令
        # if test_status:
        #     test_status = self._open_diff()

        # # 4.开始滚动
        # if test_status:
        #     test_status = self.__roll_test_step3()

        # 5.开始采集difference数据
        if test_status and self._testing:
            test_status = self._roll_check_difference()

        return test_status

    # 运动到下压起始位置(测试位置)
    def __roll_test_step1(self):
        try:
            self.current_item = 'roll_move_test_position'
            self._on_item_start(self.current_item)
            msg = '__roll_test_step1 ok'
            subordinate = self.config_obj.Roll_subordinate
            pos = self.config_obj.Roll_start_pos
            # 开始运动到指定位置
            test_status = self._Moveline(subordinate, pos, SPEED)
            if test_status is False:
                msg = 'move roll test pos fail'

            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status
        finally:
            self._on_item_end(self.current_item, test_status, str(test_status), msg, "True")
            self._on_display_msg('__roll_test_step1', msg, test_status)

    # 滚动测试->下压电机运动
    def __roll_test_step2(self):
        try:
            self.current_item = 'press_touch_product'
            self._on_item_start(self.current_item)
            msg = '__roll_test_step2 ok'
            subordinate = self.config_obj.Push_down_subordinate
            pos1 = self.config_obj.Pressure_target_pos
            pos = self.config_obj.Roll_pressure_pos
            maxN = self.config_obj.MaxN
            # 检测之前清除loadcell压力表数据
            self._clear_loadcell()
            # 运动到目标1pos
            test_status = self._press_to_pos(self.loadcell, subordinate, pos1, SPEED)
            if test_status is False:
                msg = 'roll_test_step2 run target pos1 fail'

            # 开始运动并检测压力范围
            if test_status:
                # 检测之前清除loadcell压力表数据
                # self._clear_loadcell()
                test_status = self._run_to_InitN(self.loadcell, subordinate, pos, 50, maxN)
                time.sleep(1)      # 等待压力表稳定
                if test_status is False:
                    msg = 'roll_test_step2 touch fail'

            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status
        finally:
            self._on_item_end(self.current_item, test_status, str(test_status), msg, "True")
            self._on_display_msg('__roll_test_step2', msg, test_status)

    # 滚动测试->开启滚动模式
    def __roll_test_step3(self):
        try:
            self.current_item = 'roll_test_step3'
            self._on_item_start(self.current_item)
            msg = '__roll_test_step3 fail'
            # 滚动电机运动
            subordinate = self.config_obj.Roll_subordinate
            pos = self.config_obj.Roll_pos
            # 可以测试产品时，必须使用 test_status = self._Moveline(subordinate, pos, ROLL_SPEED, False)
            test_status = self._Moveline(subordinate, pos, ROLL_SPEED, False)
            if test_status:
                msg = 'roll motor move ok '
            else:
                msg = 'roll motor move fail '
            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status
        finally:
            self.current_item = 'roll_test_step3'
            self._on_item_end(self.current_item, test_status, str(test_status), msg)
            self._on_display_msg('__roll_test_step3', msg, test_status)

    # 滚动测试->复位滚动测试动作
    def __roll_test_step4(self):
        try:
            self.current_item = 'roll_test_step4'
            self._on_item_start(self.current_item)
            msg = '__roll_test_step4 fail'
            # 下压电机复位
            test_status = self._Moveline(self.config_obj.Push_down_subordinate, 0, SPEED)
            msg = 'press moon subordinate={0} reset {1}'.format(self.config_obj.Push_down_subordinate,
                                                          'ok' if test_status else 'fail')

            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status
        finally:
            self._on_item_end(self.current_item, test_status, str(test_status), msg)
            self._on_display_msg('__roll_test_step4', msg, test_status)

    # 振动测试
    def _vibration_test(self):
        # 1.运动到振动器位置
        test_status = self.__vibration_move_step1()
        # 2.加速度无杆气缸电磁阀下
        if test_status:
            test_status = self.__vibration_test_step2()
        # 3.启动振动并采集数据
        if test_status:
            time.sleep(1)
            test_status = self._vibration_check()

        return test_status

    # 运动到振动测试位置
    def __vibration_move_step1(self):
        try:
            self.current_item = 'vibration_move_position'
            self._on_item_start(self.current_item)
            test_status = False
            msg = '__vibration_move_step1 fail'

            # 下压电机复位
            p_slav = self.config_obj.Push_down_subordinate
            test_status = self._Moveline(p_slav, 0, SPEED, False)
            # 移动电机移动到振动器位置
            r_subordinate = self.config_obj.Roll_subordinate
            test_status = self._Moveline(r_subordinate, self.config_obj.Vibrator_pos, SPEED, False)
            all_stop, run_list = self._wait_moo_stop(subordinate_list=[p_slav, r_subordinate])
            value_str = ''
            if all_stop:
                test_status = True
                value_str = "press position={0}, vibration position={1}".format(0,  self.config_obj.Vibrator_pos)
                msg = 'move to  acc pos={0} {1}'.format(self.config_obj.Vibrator_pos, 'ok' if test_status else 'fail')
            else:
                test_status = False
                msg = ''
                if [].index(p_slav) >= 0:
                    msg = "press motor not in position, subordinate={0}".format(p_slav)
                if [].index(r_subordinate) >= 0:
                    msg += "roll motor not in position, subordinate={0}".format(r_subordinate)

                value_str = str(test_status)
            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ ex.message
            return test_status
        finally:
            self._on_item_end(self.current_item, test_status, value_str, msg, "True")
            self._on_display_msg('__vibration_move_step1', msg, test_status)

    # 振动测试->加速度无杆气缸电磁阀下
    def __vibration_test_step2(self):
        try:
            self.current_item = 'vibration_down'
            self._on_item_start(self.current_item)
            msg = '__vibration_test_step2 ok'
            test_status = True
            status, set_data = self.kmlio.set_accelerated_down(False)
            if status is True:
                value, data = self.kmlio.get_accelerated_down(0, True)
                if value != 1:
                    test_status = False
                    msg = 'get_accelerated_down fail'
                else:
                    time.sleep(1)        # 等待稳定
            else:
                test_status = False
                msg = 'set_accelerated_down fail'
            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status
        finally:
            self._on_item_end(self.current_item, test_status, str(test_status), msg, "True")
            self._on_display_msg('__vibration_test_step2', msg, test_status)

    # 测试结束，正常复位
    def _test_finished(self):
        self.current_item = 'test_finished'
        self._on_item_start(self.current_item)
        # 加速度无杆气缸电磁阀上
        test_status, msg = self._accelerated_up()
        # 滚动电机复位
        if test_status:
            if self.moon_motor.CheckHomeStatus(self.config_obj.Push_down_subordinate):
                test_status, msg = self.__test_finished_step2()
            else:
                test_status = False
                msg = 'Push_down_motor fail'
        # 张紧气缸释放
        if test_status:
            test_status, msg = self.__test_finished_step3()
        # 夹爪气缸释放
        if test_status:
            test_status, msg = self.__test_finished_step4()

        try:
            # 信号等复位
            if test_status:
                self.kmlio.set_start_lamp(0)
                self.kmlio.set_reset_lamp(1)
                self.kmlio.set_red(0)
                self.kmlio.set_green(0)
                self._buzzer(2)
            else:
                self.kmlio.set_red(0)
                self._buzzer(5)
        except Exception, ex:
            msg = 'io control exception:' + ex.message
            self._on_display_msg('_test_finished', msg, False)

        self._on_item_end(self.current_item, test_status, str(test_status), msg)
        return test_status

    # 滚动电机复位
    def __test_finished_step2(self):
        try:
            msg = '__test_finished_step2 ok'
            test_status = self._Moveline(self.config_obj.Roll_subordinate, 0, SPEED)
            msg = 'roll moon reset,subordinate={0} {1}'.format(self.config_obj.Roll_subordinate, 'ok' if test_status else 'fail')
            return test_status, msg
        except Exception, ex:
            test_status = False
            msg = 'exception:'+ex.message
            return test_status, msg
        finally:
            self._on_display_msg('__test_finished_step2', msg, test_status)

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


if __name__ == "__main__":
    appconfig = APPConfigparse.APPConfigparse(r'../config.ini')
    obj = KML_garment_tester(appconfig)

    # st = '\xbe\xdc\xbe\xf8\xb7\xc3\xce\xca\xa1\xa3'
    # b = repr(st)
    # print unicode(eval(b), "gbk")

    init_st = obj.check_connect(auto=True, port_list=["COM10"])
    for i in range(0, len(init_st)):
        print init_st[i]
    while True:
        acc_info = obj.haptics_probe.read_data()
        print '-'.center(100, '-')
        print 'temperature={0}'.format(acc_info.temperature)
        print 'accelerated speed ={0},{1},{2}'.format(acc_info.xyz_acc[0], acc_info.xyz_acc[1], acc_info.xyz_acc[2])
        print 'angular speed ={0},{1},{2}'.format(acc_info.xyz_angle_acc[0], acc_info.xyz_angle_acc[1],
                                                  acc_info.xyz_angle_acc[2])
        print 'angle = {0},{1},{2}'.format(acc_info.xyx_angle[0], acc_info.xyx_angle[1], acc_info.xyx_angle[2])
        print '-'.center(100, '-')
        time.sleep(0.02)