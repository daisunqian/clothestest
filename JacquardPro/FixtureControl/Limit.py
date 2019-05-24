# -*- coding=utf-8 -*-

from ConfigParser import ConfigParser


# limit配置
class LimitConfig:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = ConfigParser()
        self.config.read(config_file)

    # 保存数据
    def _save_value(self):
        # print self.path
        with open(self.config_file, "w+") as f:
            self.config.write(f)
        self.config.read(self.config_file)    # 从读数据

    # Noise capacitance < ​0.005pF
    # Nois raw count Capacitance数据门限
    @property
    def Noise_capacitance_max(self):
        try:
            return self.config.getfloat('RawCount', 'Noise_capacitance_max')
        except Exception, ex:
            self.config.set('RawCount', 'Noise_capacitance_max', 0.005)

    # Noise capacitance < ​0.005pF
    # Nois raw count Capacitance数据门限    # true是调试模式
    @Noise_capacitance_max.setter
    def Noise_capacitance_max(self, max_value):
        self.config.set('RawCount', 'Noise_capacitance_max', max_value)
        self._save_value()

    # 75 ​< ​Baseline % < 90
    # baseline数据判定最小值
    @property
    def Baseline_min(self):
        try:
            return self.config.getfloat('RawCount', 'Baseline_min')
        except Exception, ex:
            self.config.set('RawCount', 'Baseline_min', 75)

    # 75 ​< ​Baseline % < 90
    # baseline数据判定最小值
    @Baseline_min.setter
    def Baseline_min(self, min_value):
        self.config.set('RawCount', 'Baseline_min', min_value)
        self._save_value()

    # 75 ​< ​Baseline % < 90
    # baseline数据判定最大值
    @property
    def Baseline_max(self):
        try:
            return self.config.getfloat('RawCount', 'Baseline_max')
        except Exception, ex:
            self.config.set('RawCount', 'Baseline_max', 75)

    # 75 ​< ​Baseline % < 90
    # baseline数据判定最大值
    @Baseline_max.setter
    def Baseline_max(self, min_value):
        self.config.set('RawCount', 'Baseline_max', min_value)
        self._save_value()

    # Effective Dynamic Range Capacitance >0.25pF
    # Effective Dynamic Range Capacitance数据判定最小值
    @property
    def Effective_Dynamic_Range_min(self):
        try:
            return self.config.getfloat('RawCount', 'Effective_Dynamic_Range_min')
        except Exception, ex:
            self.config.set('RawCount', 'Effective_Dynamic_Range_min', 90)

    # Effective Dynamic Range Capacitance >0.25pF
    # Effective Dynamic Range Capacitance数据判定最小值
    @Effective_Dynamic_Range_min.setter
    def Effective_Dynamic_Range_min(self, min_value):
        self.config.set('RawCount', 'Effective_Dynamic_Range_min', min_value)
        self._save_value()

    # Max Touch Capacitance > ​0.2pF
    # difference  maxCapacitance判定最小值
    @property
    def Max_Touch_Capacitance_min(self):
        try:
            return self.config.getfloat('Difference', 'Max_Touch_Capacitance_min')
        except Exception, ex:
            self.config.set('Difference', 'Max_Touch_Capacitance_min', 0.2)

    # Max Touch Capacitance >= ​0.2pF
    # difference  maxCapacitance判定最小值
    @Max_Touch_Capacitance_min.setter
    def Max_Touch_Capacitance_min(self, min_value):
        self.config.set('RawCount', 'Touch_Saturation_min', min_value)
        self._save_value()

    # Max_Touch_Capacitance_max <= 0.5
    @property
    def Max_Touch_Capacitance_max(self):
        try:
            return self.config.getfloat('Difference', 'Max_Touch_Capacitance_max')
        except Exception, ex:
            self.config.set('Difference', 'Max_Touch_Capacitance_max', 0.5)

        # Max_Touch_Capacitance_max <= 0.5

    @Max_Touch_Capacitance_max.setter
    def Max_Touch_Capacitance_max(self, max_value):
        self.config.set('RawCount', 'Max_Touch_Capacitance_max', max_value)
        self._save_value()

    #  0.70 < ​Touch Saturation < ​x0.90
    # Touch Saturation 判定最小值
    @property
    def Touch_Saturation_min(self):
        try:
            return self.config.getfloat('Difference', 'Touch_Saturation_min')
        except Exception, ex:
            self.config.set('Difference', 'Touch_Saturation_min', 70)

    #  0.70 < ​Touch Saturation < ​x0.90
    # Touch Saturation 判定最小值
    @Touch_Saturation_min.setter
    def Touch_Saturation_min(self, min_value):
        self.config.set('RawCount', 'Touch_Saturation_min', min_value)
        self._save_value()

    #  0.70 < ​Touch Saturation < ​x0.90
    # Touch Saturation 判定最小值
    @property
    def Touch_Saturation_max(self):
        try:
            return self.config.getfloat('Difference', 'Touch_Saturation_max')
        except Exception, ex:
            self.config.set('Difference', 'Touch_Saturation_max', 70)

    #  0.70 < ​Touch Saturation < ​x0.90
    # Touch Saturation 判定最小值
    @Touch_Saturation_max.setter
    def Touch_Saturation_max(self, min_value):
        self.config.set('RawCount', 'Touch_Saturation_max', min_value)
        self._save_value()

    @property
    def Baseline_raw_count(self):
        try:
            return self.config.get('RawCount', 'Baseline_raw_count')
        except Exception, ex:
            self.config.set('RawCount', 'Baseline_raw_count', '')

if __name__ == "__main__":
    appconfig = LimitConfig(r'../limit.ini')
    print appconfig.Noise_capacitance_max
    print appconfig.Baseline_min
    print appconfig.Baseline_max
    print appconfig.Effective_Dynamic_Range_min
    print 'Max_Touch_Capacitance_max=', appconfig.Max_Touch_Capacitance_max
    print appconfig.Max_Touch_Capacitance_max
    print appconfig.Touch_Saturation_min
    print appconfig.Touch_Saturation_max
    print appconfig.Baseline_raw_count


