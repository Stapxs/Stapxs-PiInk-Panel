from PIL import Image, ImageFont
import cairosvg
import io
import numpy as np

def alpha_to_color(image, color=(255, 255, 255)):
    """Set all fully transparent pixels of an RGBA image to the specified color.
    This is a very simple solution that might leave over some ugly edges, due
    to semi-transparent areas. You should use alpha_composite_with color instead.

    Source: http://stackoverflow.com/a/9166671/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """ 
    x = np.array(image)
    r, g, b, a = np.rollaxis(x, axis=-1)
    r[a == 0] = color[0]
    g[a == 0] = color[1]
    b[a == 0] = color[2] 
    x = np.dstack([r, g, b, a])
    return Image.fromarray(x, 'RGBA')

def svg(svg_path, width, height, rotation = 0):
    '''
    将 SVG 转换为 Image 对象

    Params:
        svg_path: str, SVG 文件路径
        width: int, 宽度
        height: int, 高度
    Returns:
        Image, Image 对象
    '''
    png_data = cairosvg.svg2png(
        url=svg_path,
        output_width=width,
        output_height=height
    )
    svg_image = Image.open(io.BytesIO(png_data)).convert("RGBA")
    if rotation != 0:
        svg_image = svg_image.rotate(rotation)
    svg_image = alpha_to_color(svg_image)
    # draw = ImageDraw.Draw(svg_image)
    # draw.line((width / 2 - 2, height / 2, width / 2 + 2, height / 2), fill="red")
    # draw.line((width / 2, height / 2 - 2, width / 2, height / 2 + 2), fill="red")
    return svg_image

def text(draw, text, position, font=None, font_size=16, fill="black", mode="center"):
    '''
    绘制文本

    Params:
        draw: ImageDraw, 绘制对象
        text: str, 文本内容
        position: tuple, 文本位置（中心位置）
        font: str, 字体
        font_size: int, 字体大小
        fill: str, 填充颜色
    Returns:
        tuple, 文本宽度和高度
    '''
    if font in [None, ""]:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font, font_size)
    
    text_box = draw.textbbox(position, text, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    
    if mode == "center":
        draw.text((position[0] - text_width / 2, position[1] - text_height / 2), text, font=font, fill=fill)
    elif mode == "left":
        draw.text((position[0], position[1]), text, font=font, fill=fill)

    return text_width, text_height

# ============================================

def wrap_text_for_draw(text: str, font_size: int, max_width: int, font_path = None) -> str:
    """
    根据最大宽度自动换行文本，使其适用于 draw.txt 绘制。

    Args:
        text (str): 要绘制的文本。
        font_path (str): 字体文件路径。
        font_size (int): 字体大小。
        max_width (int): 允许的最大宽度（像素）。

    Returns:
        str: 适用于 draw.txt 的自动换行文本。
    """
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)

    lines = []
    current_line = ""
    current_width = 0

    for char in text:
        char_width = font.getlength(char)  # 获取单个字符宽度
        if current_width + char_width > max_width:
            lines.append(current_line)  # 换行
            current_line = char
            current_width = char_width
        else:
            current_line += char
            current_width += char_width

    if current_line:
        lines.append(current_line)  # 添加最后一行

    return "\n".join(lines)

def truncate_text_for_draw(text: str, font_size: int, max_width: int, font_path = None) -> str:
    """截断文本并在超出宽度时添加省略号 '…'。

    Args:
        text (str): 要绘制的文本。
        font_path (str): 字体文件路径。
        font_size (int): 字体大小。
        max_width (int): 允许的最大宽度（像素）。

    Returns:
        str: 处理后的单行文本，可能带有省略号。
    """
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)
    
    # 计算整个文本的宽度
    text_width = font.getlength(text)
    
    # 如果文本宽度不超出 max_width，直接返回
    if text_width <= max_width:
        return text

    # 省略号的宽度
    ellipsis = " …"
    ellipsis_width = font.getlength(ellipsis)

    truncated_text = ""
    current_width = 0

    # 逐字符添加，直到超过 max_width - 省略号宽度
    for char in text:
        char_width = font.getlength(char)
        if current_width + char_width + ellipsis_width > max_width:
            break
        truncated_text += char
        current_width += char_width

    return truncated_text + ellipsis

def scroll_text(text: str, font_size: int, max_width: int, index: int, font_path = None, step = 1) -> tuple[int, str]:
    """在指定宽度内滚动文本，每次调用滚动一个字符。

    Args:
        text (str): 需要滚动的文本。
        font_path (str): 字体文件路径。
        font_size (int): 字体大小。
        max_width (int): 允许的最大宽度（像素）。
        index (int): 当前滚动索引（调用时应累加 step）。
        step (int): 每次滚动的步长。

    Returns:
        tuple[int, str]: (更新后的索引, 当前可见文本)
    """
    if font_path is None:
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)

    # 计算原始文本的总宽度（不含空白）
    text_width = font.getlength(text)

    # 如果文本未超出 max_width，则直接显示，无需滚动
    if text_width <= max_width:
        return 0, text  # index 设为 0，防止滚动

    # 计算额外填充空白的宽度（1/3 max_width）
    space_width = max_width // 3
    space_char = " "  # 空格字符
    current_space = ""

    # 添加空格直到达到 space_width
    while font.getlength(current_space) < space_width:
        current_space += space_char

    # 组合文本，末尾增加额外的空格
    extended_text = text + current_space
    extended_length = len(extended_text)

    # 让 index 在 0 到 extended_length 之间循环
    index = index % extended_length

    # 计算可见的滚动文本
    visible_text = ""
    current_width = 0
    i = index

    while current_width < max_width:
        char = extended_text[i % extended_length]  # 允许滚动到空白区域
        char_width = font.getlength(char)
        if current_width + char_width > max_width:
            break
        visible_text += char
        current_width += char_width
        i += 1

    # 计算新的 index，确保 index 在范围内循环
    new_index = (index + step) % extended_length

    return new_index, visible_text