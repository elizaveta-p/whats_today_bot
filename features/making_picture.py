import io
import os
import random
import textwrap

from PIL import ImageFont, Image, ImageDraw


SIZE = (1280, 1024)


def make_picture(text):
    # print(os.path.abspath(os.path.curdir))
    image = Image.Image

    background = form_part_of_pic('background', image)
    frame = form_part_of_pic('frame', image)
    character = form_part_of_pic('character', image)

    im3 = Image.alpha_composite(background, character)
    im3 = Image.alpha_composite(im3, frame)

    draw = ImageDraw.Draw(im3)
    text = text + '!!!'
    add_text(text, draw, im3)

    # font = ImageFont.truetype("data/fonts/19539.otf", 200)
    # # text = "С Днем Собаки!!!"
    # I1.text((100, 100), text, font=font, fill=(0, 0, 250))
    return im3


def image_to_bytes(im: Image.Image):
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    byte_im = buf.getvalue()
    return byte_im


def form_part_of_pic(part, image):
    data_folder = os.path.abspath(os.path.basename('data'))
    part_folder = os.path.join(os.path.join(data_folder, 'images'), part)
    # print(part_folder)
    items_filenames = os.listdir(part_folder)
    # print(items_filenames)
    item = random.choice(items_filenames)
    part = Image.open(os.path.join(part_folder, item))
    part = image.convert(part, "RGBA")
    part = part.resize(SIZE)
    return part


def add_text(text, draw, image):
    data_folder = os.path.abspath(os.path.basename('data'))
    font_folder = os.path.join(data_folder, 'fonts')
    fonts_available = os.listdir(font_folder)
    filename1 = random.choice(fonts_available)
    filename = os.path.join(font_folder, filename1)
    font = ImageFont.truetype(filename, 100)
    lines = textwrap.wrap(text, 26)
    max_len = len(max(lines, key=lambda z: len(z)))
    lines = [line.rjust(max_len, ' ') for line in lines]
    maincolor, shadowcolor = get_average_color(image)
    thickness = 2
    # print(color)
    y = 100
    for line in lines:
        w, h = font.getsize(line)
        x = (SIZE[0] - w) // 2

        draw.text((x - thickness, y - thickness), line, font=font, fill=shadowcolor)
        draw.text((x + thickness, y - thickness), line, font=font, fill=shadowcolor)
        draw.text((x - thickness, y + thickness), line, font=font, fill=shadowcolor)
        draw.text((x + thickness, y + thickness), line, font=font, fill=shadowcolor)
        draw.text((x, y), line, font=font,
                  fill=maincolor)
        y += h


def get_average_color(im: Image.Image):
    ar, ag, ab = 0, 0, 0
    pixels = im.load()
    x, y = im.size
    for i in range(x):
        for j in range(y):
            r, g, b, a = pixels[i, j]
            ar = (ar + r) // 2
            ag = (ag + g) // 2
            ab = (ab + b) // 2
    return (255 - ar, 255 - ag, 255 - ab), (ar, ag, ab)

