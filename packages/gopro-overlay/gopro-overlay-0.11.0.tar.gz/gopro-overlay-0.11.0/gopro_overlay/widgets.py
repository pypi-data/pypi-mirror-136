import functools
import importlib
import os

from PIL import Image, ImageDraw

from . import icons
from .point import Coordinate

anchors = {
    "left": "la",
    "right": "ra",
    "centre": "ma",
}


class CachingText:
    def __init__(self, at, value, font, align="left", fill=None):
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors[align]
        self.fill = fill if fill else (255, 255, 255)
        self.cache = {}

    def draw(self, image, draw):

        text = self.value()

        cached = self.cache.get(text, None)

        if cached is None:

            x0, y0, x1, y1 = self.font.getbbox(
                text=self.value(),
                stroke_width=2,
                anchor=self.anchor
            )

            if x0 < 0:
                x1 = x1 + abs(x0)
            if y0 < 0:
                y1 = y1 + abs(x0)

            backing_image = Image.new(mode="RGBA", size=(x1, y1))
            backing_draw = ImageDraw.Draw(backing_image)

            backing_draw.text(
                (abs(x0), 0),
                self.value(),
                anchor=self.anchor,
                font=self.font,
                fill=self.fill,
                stroke_width=2,
                stroke_fill=(0, 0, 0)
            )
            cached = {
                "at": Coordinate(x0 if x0 < 0 else 0, y0 if y0 < 0 else 0),
                "image": backing_image
            }
            self.cache[text] = cached

        image.alpha_composite(cached["image"], (self.at + cached["at"]).tuple())


class Text:
    def __init__(self, at, value, font, align="left", fill=None):
        self.at = at
        self.value = value
        self.font = font
        self.anchor = anchors[align]
        self.fill = fill if fill else (255, 255, 255)

    def draw(self, image, draw):
        draw.text(
            self.at.tuple(),
            self.value(),
            anchor=self.anchor,
            font=self.font,
            fill=self.fill,
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )


class Composite:

    def __init__(self, *widgets):
        self.widgets = widgets

    def draw(self, image, draw):
        for w in self.widgets:
            w.draw(image, draw)


class Drawable:
    def __init__(self, at, drawable):
        self.at = at
        self.drawable = drawable

    def draw(self, image, draw):
        image.alpha_composite(self.drawable, self.at.tuple())


def time(clock):
    return lambda: clock().strftime("%H:%M:%S.%f")[:-5]


def date(clock):
    return lambda: clock().strftime("%Y/%m/%d")


def icon(file, at, transform=lambda x: x):
    if os.path.exists(file):
        image = Image.open(file)
    else:
        with importlib.resources.path(icons, file) as f:
            image = Image.open(f)

    return Drawable(at, transform(image))


def simple_icon(at, file, size=64):
    return icon(file, at, transform=compose(
        functools.partial(transform_resize, (size, size)),
        transform_rgba,
        transform_negative
    ))


def transform_resize(target, img):
    return img.resize(target)


def transform_rgba(img):
    return img.convert("RGBA") if img.mode == "P" else img


def transform_negative(img):
    if img.mode != "RGBA":
        raise ValueError(f"I only work on RGBA, not {img.mode}")
    for i in range(0, img.size[0]):
        for j in range(0, img.size[1]):
            pixel = img.getpixel((i, j))
            img.putpixel((i, j), (255 - pixel[0], 255 - pixel[1], 255 - pixel[2], pixel[3]))
    return img


class Scene:

    def __init__(self, widgets, dimensions=None):
        self._widgets = widgets
        self._dimensions = dimensions if dimensions else (1920, 1080)

    def draw(self):
        image = Image.new("RGBA", self._dimensions, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        for w in self._widgets:
            w.draw(image, draw)

        return image


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), reversed(functions))
