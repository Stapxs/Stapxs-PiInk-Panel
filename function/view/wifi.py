from function.component.data_list import DataList
from PIL import Image, ImageDraw
from function.screen import Screen
import util.draw as drawUtil

class Wifi:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.listView: DataList = None
        self.sumStayTime = 0
        self.qualityTextIndex = 0

        self.screen = None

        self.list = [{
                "title": "MiPhone12",
                "content": "已连接 / WPA2",
                "icon": ["src/svg/locking.svg", "src/svg/locking_white.svg"],
                "quality": 61,
                "max_quality": 70,
                "signal": -60,
                "ip": "192.168.167.230"
            },
            {
                "title": "4500 块的 iPhone 16e",
                "content": "WAP3",
                "icon": ["src/svg/locking.svg", "src/svg/locking_white.svg"]
            },
            {
                "title": "ChinaNet-7W1q",
                "content": "WPA2",
                "icon": None
            },
            {
                "title": "北宋电信",
                "content": "WPA2",
                "icon": None
            },
            {
                "title": "05-KF01",
                "content": "WPA2",
                "icon": ["src/svg/locking.svg", "src/svg/locking_white.svg"]
            }
        ]
        self.connectIndex = 0

    def key_event(self, screen: Screen, key: list[str]):
        self.sumStayTime = 0
        if "down" in key:
            self.listView.next()
        elif "up" in key:
            self.listView.prev()
        elif "enter" in key:
            self.listView.interactive(self.__list_interactive)

    def mount(self, screen: Screen):
        self.screen = screen

        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        self.listView = DataList((115, 26), self.width - 120, self.height - 30, self.list)
        return self.listView.mount(image)

    def update(self, screen: Screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        image = self.__draw_connected_info(image)
        return self.listView.update(image)
    
    def unmount(self, screen: Screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        image = self.__draw_connected_info(image)
        return self.listView.unmount(image)
    
    # ===============================

    def __list_interactive(self, index: int, item: dict):
        '''
        列表交互事件
        '''
        if index == 0:
            self.screen.changeView("list")

    def __draw_connected_info(self, image):
        draw = ImageDraw.Draw(image)
        # 绘制标题
        drawUtil.text(draw, "无线局域网", (self.width - 16, 10), font_size=10, mode="right", font="src/font/fusion-pixel-10px.ttf")
        # 绘制 Wi-Fi 图标
        svg_img = drawUtil.svg("src/svg/wifi.svg", self.height // 2, self.height // 2)
        image.paste(svg_img, (12, 17))
        # 当前连接信息
        now_connect = self.list[self.connectIndex]
        drawUtil.text(draw, now_connect["title"], (12, self.height // 2 + 10), font_size=10, mode="left", font="src/font/fusion-pixel-10px.ttf")
        self.qualityTextIndex, quality_text = drawUtil.scroll_text("质量: " + str(round(now_connect["quality"] / now_connect["max_quality"] * 100, 2)) + "% (" + str(now_connect["signal"]) + "dBm)",
                                    10, 115, self.qualityTextIndex, step=2, font_path="src/font/fusion-pixel-10px.ttf")
        drawUtil.text(draw, quality_text, (12, self.height // 2 + 22), font_size=8, mode="left", font="src/font/fusion-pixel-8px.ttf")
        drawUtil.text(draw, "IP: " + now_connect["ip"], (12, self.height // 2 + 30), font_size=8, mode="left", font="src/font/fusion-pixel-8px.ttf")

        return image