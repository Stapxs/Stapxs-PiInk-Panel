from PIL import Image, ImageDraw
import math
import util.draw as drawUtil

class IconList:
    def __init__(self, screen_width: int, screen_height: int, icon_list: list):
        '''
        初始化图标列表\n
        本组件不支持自适应布局，将会绘制在整个屏幕尺寸下；请传递屏幕的大小。

        Params:
            width: int, 宽度
            height: int, 高度
            icon_list: list, 图标列表
        '''
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.icon_list = icon_list

        self.nowIndex = len(icon_list) // 2
        self.mount_step = -1
        self.change_step = -1
        self.change_next = True

    def next(self):
        self.change_next = True
        self.change_step = 0
    def prev(self):
        self.change_next = False
        self.change_step = 0

    def setIndex(self, index: int):
        self.nowIndex = index

    # ========================================

    def mount(self, image: Image):
        image = self.__draw_bar(image)
        self.mount_step = 0
        return image

    def update(self, image: Image):
        if self.mount_step >= 0 and self.mount_step < 3:
            mountStep = ["main", "list", "normal"]
            image = self.__draw_icons(image, mountStep[self.mount_step])
            self.mount_step += 1
        else:
            self.mount_step = -1
            if self.change_step >= 0:
                if self.change_step == 0:
                    image = self.__draw_icons(image, "list")
                elif self.change_step == 1:
                    self.nowIndex = (self.nowIndex + 1) % len(self.icon_list) if self.change_next else (self.nowIndex - 1) % len(self.icon_list)
                    image = self.__draw_icons(image, "normal")
                    self.change_step = -2
                self.change_step += 1
            else:
                image = self.__draw_icons(image)

        image = self.__draw_bar(image)
        return image
    
    def unmount(self, image: Image):
        if self.mount_step < 0:
            self.mount_step = 0
        if self.mount_step >= 0 and self.mount_step < 1:
            mountStep = ["big"]
            image = self.__draw_icons(image, mountStep[self.mount_step])
            self.mount_step += 1
            return False, image
        return True, image
    
    # ========================================

    def __draw_icons(self, image: Image, status="normal"):
        '''
        绘制图标
        
        Params:
            image: Image, 图片
            status: str, 图标状态<br>--> normal: 正常列表<br>--> list: 仅列表（无选中）<br>--> main: 仅中心图标<br>--> big: 仅中心图标(大)
        '''
        # 计算尺寸和位置
        icon_size = self.screen_height - 19 - (self.screen_height * 0.23) * 2       # 图标大小
        icon_top = self.screen_height * 0.15 + 19                            # 图标顶部位置
        icon_margin = icon_size / 3                                   # 图标间距
        
        # 计算可见图标数量
        show_count = math.ceil((self.screen_width - icon_size) / (icon_size + icon_margin)) + 1
        if show_count % 2 == 0:
            show_count += 1
        show_count = max(show_count, 3)
        
        # 计算布局参数
        middle_index = (show_count - 1) // 2
        group_width = show_count * icon_size + (show_count - 1) * icon_margin
        group_margin = (self.screen_width - group_width) / 2
        
        # 处理边界情况
        start_index = 0
        if self.nowIndex < middle_index:
            start_index = int(middle_index - self.nowIndex)
        
        visible_count = show_count
        if len(self.icon_list) - self.nowIndex - 1 < middle_index:
            visible_count -= int(middle_index - (len(self.icon_list) - self.nowIndex - 1))
        
        # 计算图标位置
        icon_point_list = []
        for i in range(start_index, visible_count):
            x_pos = group_margin + i * (icon_size + icon_margin)
            icon_point_list.append((x_pos, icon_top))
        
        # 准备要显示的图标列表
        draw = ImageDraw.Draw(image)
        start = max(0, self.nowIndex - middle_index)
        end = min(len(self.icon_list), self.nowIndex + middle_index + 1)
        used_icon_list = self.icon_list[start:end]
        
        # 判断中心图标的条件
        is_center_icon = lambda i: ((self.nowIndex < middle_index and self.nowIndex == i) or
                                  (self.nowIndex >= middle_index and i == middle_index))
        
        # 绘制图标
        for i in range(len(icon_point_list)):
            if i >= len(used_icon_list):
                break
                
            if is_center_icon(i):
                # 选中边框
                if status == "normal":
                    x, y = icon_point_list[i]
                    draw.rectangle((x - 6, y - 3, x + icon_size + 6, y + icon_size + 6),
                                  outline="black", width=2)
                    draw.rectangle((x - 6, y + 9, x + icon_size + 8, y + icon_size - 3),
                                  fill="white")
                    draw.rectangle((x + 3, y - 3, x + icon_size - 3, y + icon_size + 6),
                                  fill="white")
                    # 绘制图标名称
                    drawUtil.text(draw, used_icon_list[i]["name"], 
                                 (self.screen_width/2, icon_top + icon_size + 18), 
                                 font_size=10, font="src/font/fusion-pixel-10px.ttf")
                # 主图标
                if status == "big":
                    big_icon_size = self.screen_height - 19 - (self.screen_height * 0.15) * 2
                    point_move = (big_icon_size - icon_size) // 2
                    icon_image = drawUtil.svg(used_icon_list[i]["icon"], big_icon_size, big_icon_size)
                    image.paste(icon_image, (int(icon_point_list[i][0] - point_move), int(icon_point_list[i][1] - point_move)))
                else:
                    icon_image = drawUtil.svg(used_icon_list[i]["icon"], icon_size, icon_size)
                    image.paste(icon_image, (int(icon_point_list[i][0]), int(icon_point_list[i][1] + 3)))
            else:
                # 侧边图标
                if status != "main" and status != "big":
                    small_icon_size = icon_size - 12
                    icon_image = drawUtil.svg(used_icon_list[i]["icon"], small_icon_size, small_icon_size)
                    image.paste(icon_image, (int(icon_point_list[i][0] + 6), int(icon_point_list[i][1] + 6)))

        return image

    def __draw_bar(self, image: Image):
        '''
        绘制滚动条
        
        Params:
            image: Image, 图片
        '''
        draw = ImageDraw.Draw(image)
        bar_full_width = self.screen_width * 0.7
        bar_width = (bar_full_width - len(self.icon_list) - 1) / len(self.icon_list)
        # 左右边框
        bar_left = (self.screen_width - bar_full_width) / 2
        draw.rectangle((bar_left - 2, 5, bar_left + bar_full_width, 9), fill="black")
        draw.rectangle((bar_left - 1, 5, bar_left + bar_full_width - 1, 9), fill="white")
        # 滚动条
        bar_start = bar_left + self.nowIndex * bar_width + self.nowIndex
        draw.rectangle((bar_start, 5, bar_start + bar_width, 9), fill="black")

        return image

