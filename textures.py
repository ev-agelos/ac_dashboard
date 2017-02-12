import os

import ac


class Texture:

    id = None
    filename = ''
    images_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'Images')

    @classmethod
    def _load_texture(cls):
        if cls.id is None:
            cls.id = ac.newTexture(os.path.join(cls.images_dir, cls.filename))

    @classmethod
    def _draw_texture(cls, led):
        ac.glQuadTextured(led.pos_x, led.pos_y, led.width, led.height, cls.id)


class Led(Texture):

    pos_x = 144
    pos_y = 40
    width = 32
    height = 32

    def __init__(self, pos_x=None, pos_y=None, width=None, height=None):
        self.pos_x = pos_x or self.pos_x
        self.pos_y = pos_y or self.pos_y
        self.width = width or self.width
        self.height = height or self.height
        super()._load_texture()

    def draw(self):
        super()._draw_texture(self)


class RedLed(Led):

    filename = 'LedRed.png'
    pos_y = Led.pos_y + 1


class GreenLed(Led):

    filename = 'LedGreen.png'


class BlueLed(Led):

    filename = 'LedBlue.png'
    pos_y = Led.pos_y + 1


class YellowLeds(Led):

    filename = 'LedsYellow.png'
    pos_x = Led.pos_x - 15
    pos_y = Led.pos_y + 27
    width = Led.width + 311
    height = Led.height + 6
