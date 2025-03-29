from function.screen import Screen
from log4py import Logger
import importlib
import time

Logger.set_level("INFO")
log = Logger.get_logger(__name__)

class Control:
    ACCER_CHIP_ID = None         
    ACCER_DATA = []          # 数据

    def __init__(self, address = 0x19, has_hardware=False, screen: Screen = None):
        self.has_hardware = has_hardware
        self.screen = screen

        if has_hardware:
            # 动态导入库
            module = importlib.import_module("lib.DFRobot_LIS.DFRobot_LIS2DW12")
            DFRobot_LIS2DW12_I2C = getattr(module, "DFRobot_LIS2DW12_I2C")

            self.acce = DFRobot_LIS2DW12_I2C(0x01, address)
            self.acce.begin()
            self.ACCER_CHIP_ID = self.acce.get_id()
            self.acce.soft_reset()

            self.acce.set_range(self.acce.RANGE_2G)
            self.acce.set_power_mode(self.acce.CONT_LOWPWRLOWNOISE2_14BIT)
            self.acce.set_data_rate(self.acce.RATE_800HZ)

            self.acce.enable_tap_detection_on_z(True)
            self.acce.set_tap_threshold_on_z(0.2)
            self.acce.set_tap_dur(dur = 1)         # n * 1.25ms

            self.acce.set_tap_mode(self.acce.BOTH_SINGLE_DOUBLE)

            self.acce.set_int1_event(self.acce.DOUBLE_TAP)
            time.sleep(0.1)

    def run(self):
        while True:
            # # 获取数据
            # if not has_hardware:
            #     x = self.acce.read_acc_x()
            #     y = self.acce.read_acc_y()
            #     z = self.acce.read_acc_z()
            # else:
            #     x, y, z = random.uniform(-1000, 1000), random.uniform(-1000, 1000), random.uniform(-1000, 1000)
            # # 添加数据
            # Control.ACCER_DATA.append({ 'time': time.time(), 'acceleration': (x, y, z) })
            # # 移除 5s 前的数据
            # Control.ACCER_DATA = [i for i in Control.ACCER_DATA if i['time'] > time.time() - 3]

            tap = False
            event = self.acce.tap_detect()
            
            if self.screen != None and event == self.acce.S_TAP:
                log.info("mouse_click")
                self.screen.key_event(["mouse_click", "down"])
                tap = True
            elif self.screen != None and event == self.acce.D_TAP:
                log.info("mouse_double_click")
                self.screen.key_event(["mouse_double_click", "enter"])
                tap = True

            if tap == True:
                tap = False
                time.sleep(0.2)