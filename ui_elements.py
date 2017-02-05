import ac


class UIElement:

    def __init__(self, window, text='', size=(0, 0), pos=(0, 0),
                 font_color=(0, 0, 0, 0), font_size=12, bg_color=(0, 0, 0),
                 draw_bg=0, draw_border=0):
        self.id = None
        self.window = window
        self.text = text
        self.size = size
        self.pos = pos
        self.font_color = font_color
        self.font_size = font_size
        self.bg_color = bg_color
        self.draw_bg = draw_bg
        self.draw_border = draw_border

    def draw(self):
        # FIXME draw if element has value otherwise it will throw ERROR!
        ac.setSize(self.id, *self.size)
        ac.setPosition(self.id, *self.pos)
        ac.setFontColor(self.id, *self.font_color)
        ac.setFontSize(self.id, self.font_size)
        ac.setBackgroundColor(self.id, *self.bg_color)
        ac.drawBackground(self.id, self.draw_bg)
        ac.drawBorder(self.id, self.draw_border)

    def show(self):
        ac.setVisible(self.id, 1)

    def hide(self):
        ac.setVisible(self.id, 0)


class UIButton(UIElement):

    def __init__(self, *args, listener=None, **kwargs):
        super(UIElement, self).__init__(*args, **kwargs)
        self.id = ac.addButton(self.window, self.text)
        if listener is not None:
            ac.addOnClickedListener(self.id, listener)


class UILabel(UIElement):

    def __init__(self, *args, **kwargs):
        super(UIElement, self).__init__(*args, **kwargs)
        self.id = ac.addLabel(self.window, self.text)


class UIProgressBar(UIElement):

    def __init__(self, *args, **kwargs):
        super(UIElement, self).__init__(*args, **kwargs)
        self.id = ac.addProgressBar(self.window, self.text)
