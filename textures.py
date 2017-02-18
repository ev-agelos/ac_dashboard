import os

import ac


class Texture:

    images_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'Images')

    def __init__(self, pos_x=None, pos_y=None, width=None, height=None,
                 color=None, filename=''):
        self.id = ac.newTexture(os.path.join(self.images_dir, filename))
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        if self.color is not None:
            ac.glColor4f(*self.color)
        ac.glQuadTextured(self.pos_x, self.pos_y, self.width, self.height,
                          self.id)
