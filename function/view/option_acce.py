from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PIL import Image
from function.screen import Screen
from function.control import Control
import numpy as np
from scipy.interpolate import make_interp_spline
from math import sqrt
import os

class OptionAcce:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def key_event(self, screen, key):
        pass

    def mount(self, screen):
        # FIXME 这儿写死了屏幕的大小，如果需要适配其他屏幕，需要修改这个地方
        ppi = sqrt(self.width ** 2 + self.height ** 2) / 2.13
        self.fig = Figure(figsize=(48.55 / 25.4, 23.71 / 25.4), dpi=ppi)
        self.ax = self.fig.add_subplot(111)
        return self.update(screen)

    def update(self, screen: Screen):
        view_image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

        accer_data = Control.ACCER_DATA
        # 提取数据
        time = np.array([d['time'] for d in accer_data])
        time -= time[0]
        acc_x = np.array([d['acceleration'][0] for d in accer_data])
        acc_y = np.array([d['acceleration'][1] for d in accer_data])
        acc_z = np.array([d['acceleration'][2] for d in accer_data])

        time_smooth = np.linspace(time.min(), time.max(), 200)
        if len(time) >= 4:
            spl = make_interp_spline(time, acc_x, k=3)
            acc_x_smooth = spl(time_smooth)
            spl = make_interp_spline(time, acc_y, k=3)
            acc_y_smooth = spl(time_smooth)
            spl = make_interp_spline(time, acc_z, k=3)
            acc_z_smooth = spl(time_smooth)
            
            self.ax.plot(time_smooth, acc_x_smooth, linestyle='-', linewidth=1, color="black", label="X")
            self.ax.plot(time_smooth, acc_y_smooth, linestyle='--', linewidth=1, color="black", label="Y")
            self.ax.plot(time_smooth, acc_z_smooth, linestyle='-.', linewidth=1, color="black", label="Z")
        else:
            self.ax.plot(time, acc_x, linestyle='-', linewidth=1, color="black", label="X")
            self.ax.plot(time, acc_y, linestyle='--', linewidth=1, color="black", label="Y")
            self.ax.plot(time, acc_z, linestyle='-.', linewidth=1, color="black", label="Z")

        self.ax.axis('off')
        if not os.path.exists("tmp"): os.mkdir("tmp")
        self.fig.savefig("tmp/curve.png", transparent=True, bbox_inches='tight', pad_inches=0)
        self.ax.clear()

        curve_image = Image.open("tmp/curve.png")
        view_image.paste(curve_image, ((self.width - curve_image.width) // 2,
            (self.height - curve_image.height) // 2))
        
        return view_image
    
    def unmount(self, screen):
        plt.close(self.fig)
        os.remove("tmp/curve.png")
            
        return True, self.update(screen)