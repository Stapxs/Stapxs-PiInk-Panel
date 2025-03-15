import matplotlib
import matplotlib.pyplot as plt
import importlib
import traceback
from PIL import ImageDraw, Image, ImageFilter
from matplotlib.widgets import Button
from log4py import Logger

from lib.waveshare_epd import epd2in13_V3

Logger.set_level("INFO")
log = Logger.get_logger(__name__)

class screen:
    FLUSH_TIME = 0.3                # 刷新时间，与屏幕刷新时间对齐；单位：秒
    MAX_FLUSH_TIME = 10             # 最大连续刷新时间，超出之后将进入睡眠模式

    ERROR_MSG = ""
    ERROR_INFO = ""
    ERROR_VIEW = ""

    def __init__(self, width: int, height: int, debug=False):
        '''
        初始化主屏幕渲染器

        Params:
            width: int, 屏幕宽度
            height: int, 屏幕高度
            debug: bool, 是否开启调试模式
        '''
        self.width = width
        self.height = height
        self.debug = debug

        self.nowViewName = "load"
        self.lastViewName = None
        self.nowView = None
        self.changeFlag = False

        self.epd = epd2in13_V3.EPD()
        self.epd.init()
        self.epd.Clear(0xFF)

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

    # key 是个字符串数组，为了兼容连带触发，比如：click 同时也做 down 操作
    def key_event(self, key: list[str]):
        '''
        键盘事件

        Params:
            key: List[str], 键盘事件
        '''
        if self.nowView != None:
            self.nowView.key_event(self, key)

    def run(self):
        '''
        运行主屏幕渲染器
        '''
        # 初始化参数
        self.flushSumTime = 0
        mounted = False
        # 初始化 matplotlib
        fig, ax = plt.subplots()
        if not self.debug:
            # 非 Debug 模式下没有桌面环境，需要关闭交互模式
            matplotlib.use('Agg')
        else:
            plt.title("模拟绘制屏幕")
            plt.ion()
        # 添加按钮
        if self.debug:
            plt.subplots_adjust(right=0.8)
            ax_button = fig.add_axes([0.82, 0.5, 0.12, 0.08])
            button_A = Button(ax_button, '交互')
            button_A.label.set_fontproperties(matplotlib.font_manager.FontProperties(fname="src/font/fusion-pixel-8px.ttf"))
            button_A.label.set_fontsize(8)
            def on_click(event):
                print("click")
                self.key_event(["mouse_click", "down"])
            button_A.on_clicked(on_click)
            ax_button = fig.add_axes([0.82, 0.4, 0.12, 0.08])
            button_B = Button(ax_button, '确认')
            button_B.label.set_fontproperties(matplotlib.font_manager.FontProperties(fname="src/font/fusion-pixel-8px.ttf"))
            button_B.label.set_fontsize(8)
            def on_double_click(event):
                print("double click")
                self.key_event(["mouse_double_click", "enter"])
            button_B.on_clicked(on_double_click)
            plt.sca(ax)
        # 渲染循环
        while True:
            view_image = None
            try:
                # 绘制主界面
                if self.nowView == None or self.changeFlag:
                    # 如果当前视图为空，则加载到列表视图
                    if self.nowViewName == None:
                        self.nowViewName = "list"
                    # 动态导入视图类
                    module_name = f".view.{self.nowViewName}"
                    module = importlib.import_module(module_name, package=__package__)
                    cls = getattr(module, self.nowViewName.capitalize())
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
                # TODO: 屏幕休眠相关功能暂未实现
                draw = ImageDraw.Draw(view_image)
                # 在右上角绘制一个直径 4px 的圆，表示屏幕唤醒状态
                draw.ellipse((self.width - 5 - 4, 5, self.width - 5, 5 + 4), fill="black")

                # 渲染视图
                if view_image is not None:
                    ax.clear()
                    # 锐化图像
                    # view_image = view_image.filter(ImageFilter.SHARPEN)
                    if self.debug:
                        plt.imshow(view_image, cmap='gray')
                        plt.draw()
                        plt.pause(self.FLUSH_TIME)
                    else:
                        self.epd.displayPartial(self.epd.getbuffer(view_image))
                        # self.epd.display(self.epd.getbuffer(view_image))
            except ModuleNotFoundError as e:
                self.__change_view_error(f"视图 {self.nowViewName} 不存在", traceback.format_exc())
            except AttributeError as e:
                self.__change_view_error(f"视图 {self.nowViewName} 无效", traceback.format_exc())
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
        self.ERROR_MSG = msg
        self.ERROR_INFO = info
        self.ERROR_VIEW = self.lastViewName
        self.changeView("error", force=True)