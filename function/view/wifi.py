from function.component.data_list import DataList
from function.component.pop_box import PopBox
from function.screen import Screen
from PIL import Image, ImageDraw
import util.draw as drawUtil
import util.system as SystemUtil

class Wifi:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.listView: DataList = None
        self.sumStayTime = 0
        self.qualityTextIndex = 0

        self.screen = None

        wifiList = SystemUtil.get_wifi_list(True)
        nowConnect = SystemUtil.get_connected_wifi()
        # 整理数据
        self.list = []
        for wifi in wifiList:
            # 其他信息
            wifi["content"] = wifi["wpa"]
            wifi["icon"] = ["src/svg/locking.svg", "src/svg/locking_white.svg"] if wifi["password"] else None
            # 当前连接
            wifi["connected"] = False
            if nowConnect and wifi["title"] == nowConnect["title"]:
                wifi["connected"] = True
                wifi["content"] = "已连接 / " + wifi["wpa"]
                wifi["ip"] = nowConnect["ip"]
                self.connectIndex = len(self.list)
            self.list.append(wifi)
        self.connectIndex = 0

    def key_event(self, screen: Screen, key: list[str]):
        self.sumStayTime = 0
        if "down" in key:
            if self.popBox.showing:
                self.popBox.next()
            else:
                self.listView.next()
        elif "up" in key:
            if not self.popBox.showing:
                self.listView.prev()
        elif "enter" in key:
            if self.popBox.showing:
                self.popBox.interactive(self.__pop_interactive)
            else:
                self.listView.interactive(self.__list_interactive)

    def mount(self, screen: Screen):
        self.screen = screen

        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        self.listView = DataList((115, 26), self.width - 120, self.height - 30, self.list)
        self.popBox = PopBox((self.width // 5, 15), self.width // 5 * 3, self.height - 30, "提醒")
        return self.listView.mount(image)

    def update(self, screen: Screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        image = self.__draw_connected_info(image)
        image = self.listView.update(image)
        if self.popBox.showing:
            image = self.popBox.draw_mask(image)
        image = self.popBox.update(image)

        return image
    
    def unmount(self, screen: Screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        image = self.__draw_connected_info(image)
        return self.listView.unmount(image)
    
    # ===============================

    def __pop_interactive(self, button: dict, data: dict):
        '''
        弹窗交互事件
        '''
        if button["action"] == "connect":
            pass
        elif button["action"] == "disconnect":
            pass
        self.popBox.show(False)

    def __list_interactive(self, index: int, item: dict):
        '''
        列表交互事件
        '''
        if index == 0:
            self.screen.changeView("list")
        else:
            buttons = [{"text": "取消", "action": "back"}]
            if item["connected"] == False:
                buttons.append({"text": "连接", "action": "connect"})
            else:
                buttons.append({"text": "断开", "action": "disconnect"})
            self.popBox.set_buttons(buttons)
            self.popBox.set_content("是否" + ("连接到 " if item["connected"] == False else "断开 ") + item["title"] + "?")
            self.popBox.set_data(item)

            self.popBox.show()

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