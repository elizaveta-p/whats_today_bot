import io

import PIL
from PIL import ImageFont, Image, ImageEnhance, ImageDraw


def make_picture(text):
    image = Image.Image
    frame = Image.open(r'data/images/frame/frame1.png')
    frame = image.convert(frame, "RGBA")
    background = Image.open(r'data/images/background/background1.png')
    background = image.convert(background, "RGBA")
    background = background.resize(frame.size)
    dog = Image.open(r'data/images/character/character1.png')
    dog = dog.resize(background.size)
    #
    # new = Image.new("RGBA", background.size, (0, 0, 0))
    # new.show()
    # new = image.alpha_composite(new, background)
    # new.show()

    # alpha = ImageEnhance.Brightness(dog.split()[3]).enhance(0.1)
    # dog.putalpha(alpha)

    # new = Image.alpha_composite(new, dog)
    # new = Image.alpha_composite(new, frame)
    # new.show()

    im3 = Image.alpha_composite(background, dog)
    im3 = Image.alpha_composite(im3, frame)

    I1 = ImageDraw.Draw(im3)

    font = ImageFont.truetype("data/fonts/20094.ttf", 160)
    # text = "С Днем Собаки!!!"
    text = text

    I1.text((10, 10), text, font=font, fill=(0, 0, 250))

    # print(type(im3))

    return im3

    # im3.show()
    # im3.save("test.png", "PNG")


def image_to_bytes(im: Image.Image):
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    byte_im = buf.getvalue()
    return byte_im


# make_picture()
