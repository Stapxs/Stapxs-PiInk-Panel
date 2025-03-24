import importlib
import random
import time

class Control:

    ACCER_CHIP_ID = None         
    ACCER_DATA = []          # 数据

    def __init__(self, address = 0x19, virtual=False):
        self.virtual = virtual

        if not self.virtual:
            # 动态导入库
            module = importlib.import_module("lib.DFRobot_LIS.DFRobot_LIS2DW12")
            DFRobot_LIS2DW12_I2C = getattr(module, "DFRobot_LIS2DW12_I2C")

            self.acce = DFRobot_LIS2DW12_I2C(0x01, address)
            self.acce.begin()
            self.ACCER_CHIP_ID = self.acce.get_id()
            self.acce.soft_reset()

            # 基础配置
            self.acce.set_range(self.acce.RANGE_2G)
            self.acce.set_power_mode(self.acce.CONT_LOWPWRLOWNOISE1_12BIT)
            self.acce.set_data_rate(self.acce.RATE_800HZ)
            self.acce.set_filter_bandwidth(self.acce.RATE_DIV_4)
            self.acce.set_filter_path(self.acce.LPF)

    def run(self):
        while True:
            # 获取数据
            if not self.virtual:
                x = self.acce.read_acc_x()
                y = self.acce.read_acc_y()
                z = self.acce.read_acc_z()
            else:
                x, y, z = random.uniform(-1000, 1000), random.uniform(-1000, 1000), random.uniform(-1000, 1000)
            # 添加数据
            Control.ACCER_DATA.append({ 'time': time.time(), 'acceleration': (x, y, z) })
            # 移除 5s 前的数据
            Control.ACCER_DATA = [i for i in Control.ACCER_DATA if i['time'] > time.time() - 3]
            time.sleep(0.3)