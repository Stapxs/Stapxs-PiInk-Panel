from PIL import Image, ImageDraw
import math
import util.draw as drawUtil

class PopBox:
    def __init__(self, position, width: int, height: int, title: str = None):
        '''
        初始化数据列表\n
        此组件支持自适应布局，绘制在 position、width、height 控制的矩形内，不必一定要传屏幕的大小。\n
        此组件拥有一个绘制全屏遮罩的方法 draw_mask，用于绘制一个黑白相间的遮罩；如有需要，可以调用。\n
        注意：此组件没有 mount 方法，请使用 show 方法来显示。

        Params:
            position: tuple, 位置
            width: int, 宽度
            height: int, 高度
            title: str, 标题
        '''
        self.width = width
        self.height = height
        self.position = position
        self.title = title

        self.nowSelect = 0

        self.showing = False
        self.showStep = -1

    def set_buttons(self, buttons: list[dict[str, str]]):
        self.buttons = buttons
    def set_content(self, content: str):
        self.content = content
    def set_data(self, data: dict):
        self.data = data

    def next(self):
        if self.nowSelect == 1:
            self.nowSelect = 0
        else:
            self.nowSelect = 1
    
    def interactive(self, func: callable):
        '''
        交互式操作

        Params:
            func: callable, 回调函数
        '''
        if self.nowSelect < len(self.buttons):
            func(self.buttons[self.nowSelect], self.data)

    def draw_mask(self, image: Image):
        '''
        绘制遮罩
        绘制一个黑白相间的遮罩
        '''
        draw = ImageDraw.Draw(image)
        for x in range(0, image.width, 2):
            for y in range(0, image.height, 2):
                draw.point((x, y), fill="black")
        return image

    # ========================================

    def show(self, show: bool = True):
        '''
        显示或隐藏弹窗
        '''
        self.showing = show
        self.showStep = 0

    def update(self, image: Image):
        if self.showing and self.showStep > 0:
            draw = ImageDraw.Draw(image)
            window_position = (self.position[0], self.position[1],
                            self.position[0] + self.width, self.position[1] + self.height)
            # 绘制窗体
            draw.rectangle(window_position, fill="white", outline="black", width=1)
            # 绘制标题
            if self.title != None:
                drawUtil.text(draw, self.title, (self.position[0] + 10, self.position[1] + 10),
                              font_size=10, mode="left", font="src/font/fusion-pixel-10px.ttf")
            # 绘制内容
            context_position = (self.position[0] + 10, self.position[1] + 25)
            if self.title == None:
                context_position = (self.position[0] + 10, self.position[1] + 10)
            context = drawUtil.wrap_text_for_draw(self.content, 8, self.width - 11, "src/font/fusion-pixel-8px.ttf")
            drawUtil.text(draw, context, context_position, font_size=8, mode="left", font="src/font/fusion-pixel-8px.ttf")
            # 绘制按钮（最多两个）
            draw.line((self.position[0] + 10, self.position[1] + self.height - 35, self.position[0] + self.width - 10, self.position[1] + self.height - 35), fill="black")
            button_width = (self.width - 20) / 2 - 10
            for i in range(min(2, len(self.buttons))):
                real_index = 1 if i == 0 else 0
                # 倒序绘制按钮，保证只有一个按钮的时候按钮居右
                button_position = (self.position[0] + 15 + (button_width + 10) * real_index, self.position[1] + self.height - 25,
                                   self.position[0] + 15 + (button_width + 10) * real_index + button_width, self.position[1] + self.height - 10)
                if self.nowSelect == i:
                    draw.rectangle(button_position, fill="black", outline="black", width=1)
                # 绘制按钮文本
                button_text = self.buttons[i]["text"]
                text_color = "white" if self.nowSelect == i else "black"
                button_text_position = (button_position[0] + button_width / 2, button_position[1] + 5)
                drawUtil.text(draw, button_text, button_text_position, font_size=8, mode="center", fill=text_color, font="src/font/fusion-pixel-8px.ttf")
        self.showStep += 1
        return image
    
    def unmount(self, image: Image):
        return True, self.update(image)