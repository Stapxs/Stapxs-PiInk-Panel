from function.component.icon_list import IconList
from PIL import Image
from function.screen import Screen

class List:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.listView: IconList = None
        self.sumStayTime = 0

        self.list = [{
                "icon": "src/svg/wifi.svg",
                "name": "Wi-Fi",
                "view": "wifi"
            },
            {
                "icon": "src/svg/bluetooth_link.svg",
                "name": "蓝牙",
                "view": "bluetooth"
            },
            {
                "icon": "src/svg/settings.svg",
                "name": "设置",
                "view": "setting"
            },
            {
                "icon": "src/svg/home.svg",
                "name": "主页",
                "view": "home"
            },
            {
                "icon": "src/svg/info.svg",
                "name": "关于",
                "view": "about"
            },
            {
                "icon": "src/svg/close.svg",
                "name": "重启",
                "view": "reboot"
            },
        ]
        self.homeIndex = 3

    def key_event(self, screen: Screen, key: list[str]):
        self.sumStayTime = 0
        if "down" in key:
            self.listView.next()
        elif "up" in key:
            self.listView.prev()
        elif "mouse_double_click" in key:
            screen.changeView(self.list[self.listView.nowIndex]["view"])

    def mount(self, screen: Screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

        self.listView = IconList(self.width, self.height, self.list)
        return self.listView.mount(image)

    def update(self, screen: Screen):
        self.sumStayTime += screen.lastRenderTime
        if self.sumStayTime > 7:
            self.listView.setIndex(self.homeIndex)
            screen.changeView("home")

        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        return self.listView.update(image)
    
    def unmount(self, screen: Screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        return self.listView.unmount(image)