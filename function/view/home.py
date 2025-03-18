from PIL import Image, ImageDraw
import util.draw as drawUtil
from function.screen import Screen

class Home:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def key_event(self, screen, key):
        if "enter" in key:
            screen.changeView("list")

    def mount(self, screen: Screen):
        return self.update(screen)

    def update(self, screen):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        drawUtil.text(draw, "Hello, World!", (20, 20), mode="left",
                    font_size=10, font="src/font/fusion-pixel-10px.ttf")

        return image
    
    def unmount(self, screen):
        return True, self.update(screen)