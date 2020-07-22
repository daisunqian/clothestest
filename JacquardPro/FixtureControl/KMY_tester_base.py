# -*- coding=utf-8 -*-

from FixtureControl.KML_tester_base import *


# 背包测试基类
class KMY_tester_base(KML_tester_base):

    def __init__(self, config, limit_config):
        super(KMY_tester_base, self).__init__(config, limit_config)
        self.camera = None

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

                    # 6. LED测试
                    if check_dut_status and self._testing and test_status:
                        test_status = self._led_test()
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

    # led 测试
    def _led_test(self):
        # 白光测试
        test_status = self._led_while_test()
        # 关闭
        self._led_close()

        return test_status

    # led白光
    def _led_while_test(self):
        try:
            self.current_item = 'led_test'
            self._on_item_start(self.current_item)
            msg = ''
            # 发送点led命令---点亮成白光
            self.mcu.start_led()
            test_status = self._on_manual_window('confirm led',
                                          'Observe the led, please confirm whether the white led is lit or not?')

            msg = 'white Led test ok' if test_status else 'white Led test fail'

            return test_status
        except Exception, ex:
            test_status = False
            msg = 'exception:'+str(ex)
            return test_status
        finally:
            self._on_item_end(self.current_item, test_status, str(test_status), msg)
            self._on_display_msg('led_test', msg, test_status)

    # 关闭
    def _led_close(self):
        try:
            test_status = True
            # 发送点led命令---关闭灯光
            self.mcu.start_led("00", "00", "00")
            msg = 'led close'
            return True
        except Exception, ex:
            test_status = False
            msg = 'exception:'+str(ex)
            return test_status
        finally:
            self._on_display_msg('_led_close', msg, test_status)

        # 下压到指定位置，并且这个位置不会接触到dut,如果有接触，自动调整到不接触

    # def _press_to_pos(self, loadcell, subordinate, pos, speed, timeout=30):
    #     # 采集loadcell数据，如果力>=minN,立即停止,判断当前力是否在min-max之间
    #     try:
    #         if isinstance(loadcell, LocalCell):
    #             dit_pos = pos
    #             self._Moveline(subordinate, dit_pos, speed, False)
    #
    #             endtime = time.time() + timeout
    #             no_data_cnt = 0
    #             loadcell.ClearBuffer()  # 执行采集前清缓存？还是每次采集清除缓存
    #             while time.time() <= endtime:
    #                 try:
    #                     if self._testing is False:
    #                         self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                         self._on_display_msg('_press_to_pos', 'stop test', False)
    #                         return False
    #
    #                     str_n = loadcell.ReadLocalCellSigle(timeout=0.02)
    #                     if str_n == 'None':
    #                         no_data_cnt = no_data_cnt + 1
    #                         time.sleep(0.01)
    #                     else:
    #                         cuurent_n = float(str_n)
    #                         no_data_cnt = 0
    #                         if cuurent_n >= 0.1:
    #                             self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                             # datas = self.moon_motor.GetMoonsStatus(subordinate, 8)
    #                             # dit_pos = dit_pos - 500 if pos > 0 else dit_pos + 500  # 负号表示方向
    #                             # self._Moveline(subordinate, dit_pos, speed)
    #                             return True  # 只执行一次回退
    #                         else:
    #                             if self.moon_motor.StopStatus(subordinate):
    #                                 # 运动已经停止，且压力未大于0,保存当前pos数据
    #                                 # self.config_obj.Pressure_target_pos = dit_pos
    #                                 self.display_msg.emit('_press_to_pos to pos =:{0}'.format(dit_pos), True)
    #                                 return True
    #                     # 连续5次读不到loadcell数据(有可能loadcell掉线或坏了),退出
    #                     if no_data_cnt >= 5:
    #                         self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                         # self.display_msg.emit('_press_to_pos fail', False)
    #                         self._on_display_msg('_press_to_pos', 'collect loadcell fail, no_data_cnt=5', False)
    #                         return False
    #                 except Exception, ex:
    #                     self._on_display_msg('_press_to_pos', 'exception:{0}'.format(ex.message), False)
    #         else:
    #             self._on_display_msg('_press_to_pos', 'loadcell object is not LocalCell type', False)
    #         return False
    #     finally:
    #         if isinstance(loadcell, LocalCell):
    #             loadcell.CloseSerial()
    #
    # # 运动到指定力位置
    # # loadcell 读压力值的loadcell对象
    # # subordinate 电机地址
    # # pos 运动距离
    # # speed 运动速度
    # # toN 目标压力
    # # deviation 目标压力误差百分比，默认是5%
    # def _run_to_InitN(self, loadcell, subordinate, pos, speed, toN, deviation=5, timeout=30):
    #     # 采集loadcell数据，如果力>=minN,立即停止,判断当前力是否在min-max之间
    #     try:
    #         if isinstance(loadcell, LocalCell):
    #             dit_pos = pos
    #             minN = toN - toN * deviation / 100.00
    #             # maxN = toN + toN * 50 / 100.00
    #             maxN = toN + 0.3
    #             self._Moveline(subordinate, dit_pos, speed, False)
    #             endtime = time.time() + timeout
    #             no_data_cnt = 0
    #             loadcell.ClearBuffer()  # 执行采集前清缓存？还是每次采集清除缓存
    #             while True:
    #                 try:
    #                     if self._testing is False:
    #                         self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                         self._on_display_msg('_run_to_InitN', 'stop test', False)
    #                         return False
    #
    #                     if time.time() > endtime:
    #                         self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                         return False
    #                     str_n = loadcell.ReadLocalCellSigle(timeout=0.01)
    #                     print 'str_n = {0}'.format(str_n).center(100, '-')
    #                     if str_n == 'None':
    #                         no_data_cnt = no_data_cnt + 1
    #                         # time.sleep(0.02)
    #                     else:
    #                         try:
    #                             cuurent_n = float(str_n)
    #                             no_data_cnt = 0
    #                             if cuurent_n >= MAX_N:
    #                                 self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                                 str_n = loadcell.ReadLocalCellSigle(timeout=0.01)
    #                                 cuurent_n = float(str_n)
    #                                 if cuurent_n >= MAX_N:
    #                                     self._on_display_msg('_run_to_InitN', 'loadcell data > max_N={0}'.format(MAX_N),
    #                                                          False)
    #                                     return False
    #                             if cuurent_n >= minN:
    #                                 self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                                 speed = 100
    #                                 if cuurent_n <= maxN:
    #                                     return True
    #                                 else:
    #                                     # 大于最大，必须回退
    #                                     # datas = self.moon_motor.GetMoonsStatus(subordinate, 8)
    #                                     dit_pos = dit_pos - 5000 if pos > 0 else dit_pos + 5000  # 负号表示方向
    #                                     self._Moveline(subordinate, dit_pos, speed, False)
    #                             else:
    #                                 # 已到位，必须增加运动距离，达到指定力附近
    #                                 # print self.moon_motor,
    #                                 if self.moon_motor.StopStatus(subordinate):
    #                                     dit_pos = dit_pos + 5000 if pos > 0 else dit_pos - 5000  # 负号表示方向
    #                                     self._Moveline(subordinate, dit_pos, speed, False)
    #                         except Exception, ex:
    #                             no_data_cnt = no_data_cnt + 1
    #
    #                     # 连续5次读不到loadcell数据(有可能loadcell掉线或坏了),退出
    #                     if no_data_cnt >= 10:
    #                         self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                         self._on_display_msg('_run_to_InitN', 'collect loadcell fail, no_data_cnt=5', False)
    #                         return False
    #                 except Exception, ex:
    #                     self.moon_motor.SetMoonsImmediatelyStop(subordinate)
    #                     self._on_display_msg('_run_to_InitN', 'exception:{0}'.format(ex.message), False)
    #         else:
    #             self._on_display_msg('_run_to_InitN', 'loadcell object is not LocalCell type', False)
    #         return False
    #     finally:
    #         if isinstance(loadcell, LocalCell):
    #             loadcell.CloseSerial()


if __name__ == "__main__":
    # ls = [10,9,10,9,9,9,9,9,9,8,8,8,8,7,7,7,7,7,6,6,6,6,6,5,5,5,5,5,5,4,4,4,4,3,3,3,3,2,2,2,2,1,1,1,1]
    # ls_1 = list(set(ls))
    # ls_1.sort(key=ls.index)

    # index = ls_1.index(9)
    # if index > 0:
    #     l0_l11 = ls_1[index:index + 8]

    appconfig = APPConfigparse.APPConfigparse(r'../config.ini')
    obj = KML_tester_base(appconfig)
    init_st = obj.check_connect()
    for i in range(0, 6):
        print init_st[i]