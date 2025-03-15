from PIL import Image, ImageDraw
import util.draw as drawUtil
import re

class Error:

    def __init__(self, width, height, debug=False):
        self.width = width
        self.height = height
        self.debug = debug

        self.rotation = 0

        self.titleScrollIndex = 0

    def key_event(self, screen, key):
        if "mouse_double_click" in key:
            screen.changeView(screen.ERROR_VIEW)
            screen.ERROR_VIEW = ""

    def mount(self, screen):
        return self.update(screen)

    def update(self, screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

        draw = ImageDraw.Draw(image)
        svg_path = 'src/svg/gear-solid.svg'
        svg_width = svg_height = self.height - 20
        position = (int(1 - (svg_width / 2)), 10)

        # 绘制 SVG 到图像
        self.rotation -= 6
        svg_image = drawUtil.svg(svg_path, svg_width, svg_height, self.rotation)
        image.paste(svg_image, position)

        # 绘制错误提醒
        drawUtil.text(draw, "错误中断", (svg_width // 2 + 20, 10), 
                      font="src/font/fusion-pixel-10px.ttf", font_size=10, fill="black", mode="left")
        text_allow_width = self.width - svg_width // 2 - 30
        self.titleScrollIndex, errorMsg = drawUtil.scroll_text(screen.ERROR_MSG, 8, text_allow_width, self.titleScrollIndex, step=2, font_path="src/font/fusion-pixel-8px.ttf")
        drawUtil.text(draw, errorMsg, (svg_width // 2 + 20, 30),
                      font="src/font/fusion-pixel-8px.ttf", font_size=8, fill="black", mode="left")
        # 画条分割线
        errorInfo = drawUtil.wrap_text_for_draw(self.__extract_first_traceback_line(screen.ERROR_INFO), 8, text_allow_width, font_path="src/font/fusion-pixel-8px.ttf")
        draw.line((svg_width // 2 + 20, 45, self.width - 10, 45), fill="black", width=1)
        drawUtil.text(draw, errorInfo, (svg_width // 2 + 20, 50),
                      font="src/font/fusion-pixel-8px.ttf", font_size=8, fill="black", mode="left")
        # 底部提醒文本
        notice_left = (self.width - svg_width // 2 + 20) // 2 + svg_width // 2 - 10
        drawUtil.text(draw, "> 双击忽略错误重新加载 <", (notice_left, self.height - 25), 
                      font="src/font/fusion-pixel-8px.ttf", font_size=8, fill="black")
        
        return image
    
    def unmount(self, screen):
        return True, self.update(screen)
    
    # ============================================
    
    def __extract_first_traceback_line(self, tb_str):
        """提取 Traceback 信息中的第一个文件路径及行号"""
        match = re.search(r'File "(.+?)", line (\d+)', tb_str)
        if match:
            return f"{match.group(1)}:{match.group(2)}"
        return "未知的错误"