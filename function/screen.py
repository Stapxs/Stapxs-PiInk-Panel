import matplotlib
import matplotlib.pyplot as plt
import importlib
import traceback
import time
from PIL import ImageDraw, Image
from matplotlib.widgets import Button
from log4py import Logger

Logger.set_level("INFO")
log = Logger.get_logger(__name__)

class Screen:
    DEBUG = False

    FLUSH_TIME = 0.7                # 刷新时间。模拟显示的时候以及跳过帧的时候会用；单位：秒
    MAX_FLUSH_TIME = 20             # 最大连续刷新时间。超出之后将进入睡眠模式；单位：秒

    ERROR_MSG = ""                  # 错误信息
    ERROR_INFO = ""                 # 错误详情
    ERROR_VIEW = ""                 # 错误视图

    CURRENT_PATH = ""               # 当前路径

    def __init__(self, width: int, height: int, debug=False, run_mode='virtual', current_path=""):
        '''
        初始化主屏幕渲染器

        Params:
            width: int, 屏幕宽度
            height: int, 屏幕高度
            debug: bool, 是否开启调试模式
        '''
        # Screen 基础信息
        Screen.DEBUG = debug                        # 调试模式
        Screen.CURRENT_PATH = current_path          # 运行路径
        self.run_mode = run_mode                    # 运行模式
        self.width = width                          # 屏幕宽度
        self.height = height                        # 屏幕高度

        # Screen 状态信息
        # self.nowViewName = "load"
        self.nowViewName = "list"                   # 当前所在视图名称
        self.lastViewName = None                    # 上个视图名称
        self.nowView = None                         # 当前所在视图实例
        self.changeFlag = False                     # 视图切换标志

        # Screen 时间信息
        self.activeTime = 0                         # 屏幕活跃时长
        self.isSleep = False                        # 是否睡眠
        self.lastRenderTime = 0                     # 上一帧渲染时长（给一些需要计时的视图使用）

        # 初始化电子墨水屏
        if run_mode in ['hardware', 'all']:
            # 动态导入库
            module = importlib.import_module("lib.waveshare_epd.epd2in13_V3")
            EPD = getattr(module, "EPD")
            self.epd = EPD()
            self.epd.init()
            self.epd.Clear(0xFF)

    def wakeUpScreen(self):
        '''
        唤醒屏幕
        '''
        # 重置屏幕唤醒时间
        self.activeTime = 0
        # 重置屏幕休眠状态
        if self.isSleep:
            log.info("屏幕唤醒……")
            self.isSleep = False
            self.epd.init()

    def changeView(self, viewName: str, force=False):
        '''
        切换当前视图

        Params:
            viewName: str, 视图名称
        '''
        if viewName == self.nowViewName and not force:
            # 如果视图名称相同，则不切换; force 参数为 True 时强制切换
            return
        self.lastViewName = self.nowViewName
        self.nowViewName = viewName
        self.changeFlag = True

    def key_event(self, key: list[str]):
        '''
        键盘事件<br>
        PS：key 是个字符串数组，为了兼容连带触发，比如：click 同时也做 down 操作

        Params:
            key: List[str], 键盘事件
        '''
        if self.activeTime >= Screen.MAX_FLUSH_TIME:
            if "enter" in key:
                self.wakeUpScreen()
            else:
                return
        elif self.nowView != None:
            self.activeTime = 0
            self.nowView.key_event(self, key)

    def run(self):
        '''
        运行主屏幕渲染
        '''
        # 初始化参数
        screenRenderTime = None
        screenFullRenderTime = 0
        mounted = False
        # 初始化 matplotlib
        self.fig, self.ax = plt.subplots()
        if self.run_mode == 'hardware':
            # 纯硬件显示模式下不显示窗口绘制
            matplotlib.use('Agg')
        else:
            plt.ion()
        log.info("当前启用的渲染器：" + matplotlib.get_backend())
        # 添加按钮
        if self.DEBUG:
            plt.subplots_adjust(right=0.8)
            ax_button = self.fig.add_axes([0.82, 0.5, 0.12, 0.08])
            button_A = Button(ax_button, '交互')
            button_A.label.set_fontproperties(matplotlib.font_manager.FontProperties(fname="src/font/fusion-pixel-8px.ttf"))
            button_A.label.set_fontsize(8)
            def on_click(_):
                print("click")
                self.key_event(["mouse_click", "down"])
            button_A.on_clicked(on_click)
            ax_button = self.fig.add_axes([0.82, 0.4, 0.12, 0.08])
            button_B = Button(ax_button, '确认')
            button_B.label.set_fontproperties(matplotlib.font_manager.FontProperties(fname="src/font/fusion-pixel-8px.ttf"))
            button_B.label.set_fontsize(8)
            def on_double_click(_):
                print("double click")
                self.key_event(["mouse_double_click", "enter"])
            button_B.on_clicked(on_double_click)
            plt.sca(self.ax)
        # 渲染循环
        while True:
            screenRenderTime = time.time()
            view_image = None
            try:
                # 绘制主界面
                if self.isSleep == False:
                    if self.nowView == None or self.changeFlag:
                        # 如果当前视图为空，则加载到列表视图
                        if self.nowViewName == None:
                            self.nowViewName = "list"
                        # 动态导入视图类
                        module_name = f".view.{self.nowViewName}"
                        module = importlib.import_module(module_name, package=__package__)
                        cls = getattr(module, self.nowViewName.title().replace("_", ""))
                        # 卸载 view 前，调用一次 unmount 方法，此方法负责卸载动画以及资源释放
                        # PS: 为了防止 unmount 方法错误；在弹出错误视图时，不调用 unmount 方法
                        if self.nowView != None and self.nowViewName != "error":
                            mounted, view_image = self.nowView.unmount(self)
                        if mounted or self.nowView == None or self.nowViewName == "error":
                            log.info("载入视图 " + self.nowViewName + " 成功。")
                            self.changeFlag = False
                            mounted = False
                            # 载入新的 view
                            self.nowView = cls(self.width, self.height)
                            # 首次加载 view，调用一次 mount 方法，此方法负责载入动画以及初始化
                            view_image = self.nowView.mount(self)
                    else:
                        view_image = self.nowView.update(self)

                    if view_image is None:
                        view_image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

                    # 绘制屏幕状态指示器
                    if self.activeTime < Screen.MAX_FLUSH_TIME - 1:
                        draw = ImageDraw.Draw(view_image)
                        # 在右上角绘制一个直径 4px 的圆，表示屏幕唤醒状态
                        draw.ellipse((self.width - 5 - 4, 5, self.width - 5, 5 + 4), fill="black")

                    # 渲染视图
                    if view_image is not None:
                        self.ax.clear()
                        # 显示窗口绘制
                        if self.run_mode in ['virtual', 'all']:
                            view_image = view_image.convert('1')
                            plt.imshow(view_image, cmap='gray')
                            plt.draw()
                            plt.show()
                            if self.run_mode == 'virtual':
                                # 在没有硬件的情况下模仿渲染延迟
                                plt.pause(Screen.FLUSH_TIME)
                        # 硬件绘制
                        if self.run_mode != 'virtual':
                            if screenFullRenderTime > 60 * 3:
                                # 如果连续渲染时间超过 3 分钟，则完整刷新屏幕
                                self.epd.display(self.epd.getbuffer(view_image))
                                screenFullRenderTime = 0
                            else:
                                self.epd.displayPartial(self.epd.getbuffer(view_image))
                # 睡眠判断
                if self.run_mode in ['virtual', 'all']:
                    # 因为要等渲染完成之后才能休眠屏幕，所以睡眠判断在最后
                    if self.activeTime > Screen.MAX_FLUSH_TIME:
                        if self.isSleep == False:
                            log.info("触发屏幕休眠……")
                            self.isSleep = True
                            self.epd.sleep()
                        plt.pause(1)
                # 计算渲染时间，加载时不算
                renderTime = round(time.time() - screenRenderTime, 2)
                self.lastRenderTime = renderTime
                if self.isSleep != True:
                    log.info("渲染耗时：" + str(renderTime))
                if not self.changeFlag:
                    self.activeTime += renderTime
                    if not self.isSleep:
                        screenFullRenderTime += renderTime

            except Exception as e:
                traceback.print_exc()
                self.__change_view_error(str(e), traceback.format_exc())

    # ============================================

    def __change_view_error(self, msg: str, info: str):
        '''
        切换到错误视图

        Params:
            msg: str, 错误信息
            info: str, 错误详情
        '''
        Screen.ERROR_MSG = msg
        Screen.ERROR_INFO = info
        Screen.ERROR_VIEW = self.lastViewName
        self.changeView("error", force=True)