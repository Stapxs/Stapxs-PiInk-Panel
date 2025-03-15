from PIL import Image, ImageDraw
import util.draw as drawUtil
from function.screen import screen as Screen

class Load:

    def __init__(self, width, height, debug=False):
    
        self.width = width
        self.height = height
        self.debug = debug

        self.sumTime = 0
        self.size = 80

    def key_event(self, screen, key):
        screen.changeView("list")

    def mount(self, screen):
        return self.update(screen)

    def update(self, screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))

        draw = ImageDraw.Draw(image)
        svg_path = 'src/svg/ss-team.svg'

        # 每次渲染都放大一点
        if self.sumTime <= 1:
            self.size -= 4
        svg_width = svg_height = self.height - self.size
        # 居中
        position = (int((self.width - svg_width) / 2), int((self.height - svg_height) / 2))

        # 绘制 SVG 到图像
        svg_image = drawUtil.svg(svg_path, svg_width, svg_height)
        image.paste(svg_image, position)

        self.sumTime += Screen.FLUSH_TIME
        if self.sumTime >= 1:
            screen.changeView("list")

        return image
    
    def unmount(self, screen):
        return True, self.update(screen)