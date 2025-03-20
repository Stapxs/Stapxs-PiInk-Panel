from lib.DFRobot_LIS.DFRobot_LIS2DW12 import *

class Control:

    ACCER_CHIP_ID = None         
    ACCER_DATA = []          # 数据

    def __init__(self, address = 0x19):
        ic2_bus = 0x01

        self.acce = DFRobot_LIS2DW12_I2C(ic2_bus, address)
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
            x = self.acce.read_acc_x()
            y = self.acce.read_acc_y()
            z = self.acce.read_acc_z()
            # 添加数据
            self.ACCER_DATA.append((x, y, z), time.time())
            # 移除 5s 前的数据
            self.ACCER_DATA = [data for data in self.ACCER_DATA if data[1] > time.time() - 5]
