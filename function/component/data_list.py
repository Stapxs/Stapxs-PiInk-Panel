from PIL import Image, ImageDraw
import math
import util.draw as drawUtil

class DataList:
    def __init__(self, position, width: int, height: int, data_list: list):
        '''
        初始化数据列表

        Params:
            width: int, 宽度
            height: int, 高度
            data_list: list, 数据列表
        '''
        self.width = width
        self.height = height
        self.position = position
        self.data_list =  [{"title": "返回", "content": "", "icon": None }] + data_list

        self.nowIndex = -1
        self.selectedIndex = 0
        self.mount_step = -1
        self.change_step = -1
        self.change_next = True

    def next(self):
        self.change_next = True
        self.change_step = 0
    def prev(self):
        self.change_next = False
        self.change_step = 0

    def interactive(self, func: callable):
        '''
        交互式操作

        Params:
            func: callable, 回调函数
        '''
        if self.nowIndex >= 0:
            func(self.nowIndex, self.data_list[self.nowIndex])

    # ========================================

    def mount(self, image: Image):
        image = self.__draw_bar(image)
        self.mount_step = 0
        return image

    def update(self, image: Image):
        if self.change_step >= 0:
            self.nowIndex = (self.nowIndex + 1) % len(self.data_list) if self.change_next else (self.nowIndex - 1) % len(self.data_list)
            self.change_step = -2
        
        image = self.__draw_list(image)
        image = self.__draw_bar(image)

        if self.mount_step >= 0:
            self.nowIndex = 0
            self.mount_step = -1

        return image
    
    def unmount(self, image: Image):
        if self.mount_step == -1:
            self.mount_step = -2
            self.nowIndex = -1
            return False, self.update(image)
        else:
            return True, self.update(image)
    
    # ========================================

    def __draw_list(self, image: Image, status="normal"):
        '''
        绘制数据列表
        
        Params:
            image: Image, 图片
            status: str, 状态
        '''
        show_count = self.height // 28      # 每页显示的列表项数量
        # 截取显示的数量
        visible_items, cursor_position = self.__get_visible_items(self.data_list, self.nowIndex, show_count)
        for i in range(len(visible_items)):
            item = visible_items[i]
            position = (self.position[0], self.position[1] + i * 28)
            image = self.__draw_item(image, item, position, i == cursor_position)
        return image
    
    def __get_visible_items(self, lst, selected_index, page_size=3):
        list_size = len(lst)
        raw_selected_index = selected_index

        if list_size <= page_size:
            return lst, selected_index  # 直接返回整个列表，选中索引不变

        # 限制 selected_index 在合理范围
        selected_index = max(0, min(selected_index, list_size - 1))

        # 计算起始索引
        if selected_index < page_size - 1:
            start_index = 0
        elif selected_index > list_size - page_size:
            start_index = list_size - page_size
        else:
            start_index = selected_index - (page_size // 2)

        # 计算选中项在可视列表中的索引
        visible_selected_index = selected_index - start_index
        # -1 是未选中的特殊状态
        if raw_selected_index == -1:
            visible_selected_index = -1

        return lst[start_index:start_index + page_size], visible_selected_index
    
    def __draw_item(self, image: Image, item, position, selected=False):
        '''
        绘制列表项
        
        Params:
            image: Image, 图片
            item: dict, 项
            position: tuple, 位置
            selected: bool, 是否选中
        '''
        draw = ImageDraw.Draw(image)
        # 列表项底色
        draw.rectangle((position[0], position[1],position[0] + self.width - 12, position[1] + 24), fill="black")
        draw.rectangle((position[0] + 1, position[1],position[0] + self.width - 13, position[1] + 24), fill="white")
        if selected:
            draw.rectangle((position[0] + 1, position[1],position[0] + self.width - 13, position[1] + 24), fill="black")
        # 列表项
        font_color = "white" if selected else "black"
        text_real_width = self.width - 20
        if item["icon"] != None:
            text_real_width -= 13
        if not selected:
            title_text = drawUtil.truncate_text_for_draw(item["title"], 10, text_real_width, "src/font/fusion-pixel-10px.ttf")
            drawUtil.text(draw, title_text, (position[0] + 4 ,position[1]), font="src/font/fusion-pixel-10px.ttf", font_size=10, fill=font_color, mode="left")
        else:
            self.selectedIndex, title_text = drawUtil.scroll_text(item["title"], 10, text_real_width, self.selectedIndex, step=2, font_path="src/font/fusion-pixel-10px.ttf")
            drawUtil.text(draw, title_text, (position[0] + 4 ,position[1]), font="src/font/fusion-pixel-10px.ttf", font_size=10, fill=font_color, mode="left")
        if item["content"] != "":
            drawUtil.text(draw, item["content"], (position[0] + 10, position[1] + 11), font="src/font/fusion-pixel-8px.ttf", font_size=8, fill=font_color, mode="left")
        # 密码图标
        if item["icon"] != None:
            if selected:
                icon_image = drawUtil.svg(item["icon"][1], 12, 12, fill_background=False)
            else:
                icon_image = drawUtil.svg(item["icon"][0], 12, 12)
            image.paste(icon_image, (position[0] + text_real_width + 5, position[1] + 6))

        return image

    def __draw_bar(self, image: Image):
        '''
        绘制滚动条
        
        Params:
            image: Image, 图片
        '''
        draw = ImageDraw.Draw(image)
        nowIndex = max(0, self.nowIndex)
        bar_full_height = self.height
        bar_height = (bar_full_height - 2) // len(self.data_list)
        # 滚动条最底层
        draw.rectangle((self.position[0] + self.width - 4, self.position[1],
                        self.position[0] + self.width, self.position[1] + self.height), fill="black")
        # 滚动条背景色（高度缩进 1px）
        draw.rectangle((self.position[0] + self.width - 4, self.position[1] + 1,
                        self.position[0] + self.width, self.position[1] + self.height - 1), fill="white")
        # 滚动条
        draw.rectangle((self.position[0] + self.width - 4, self.position[1] + bar_height * nowIndex + 2,
                        self.position[0] + self.width, self.position[1] + bar_height * (nowIndex + 1)), fill="black")
        return image

