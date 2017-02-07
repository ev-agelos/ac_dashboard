import ac


class UIElement:

    def __init__(self, window, text='', size=(20, 20), pos=(0, 0),
                 font_color=(1, 1, 1, 1), font_size=12, bg_color=(1, 1, 1),
                 draw_bg=1, bg_opacity=0.6, draw_border=0):
        self.id = None
        self.window = window
        self.text = text
        self.size = size
        self.pos = pos
        self.font_color = font_color
        self.font_size = font_size
        self.bg_color = bg_color
        self.draw_bg = draw_bg  # 0 (transparent) or 1 (not trasparent)
        self.bg_opacity = bg_opacity  # 0 <= float <= 1
        self.draw_border = draw_border

    def draw(self):
        ac.setSize(self.id, *self.size)
        ac.setPosition(self.id, *self.pos)
        ac.setFontColor(self.id, *self.font_color)
        ac.setFontSize(self.id, self.font_size)
        ac.setBackgroundColor(self.id, *self.bg_color)
        ac.setBackgroundOpacity(self.id, self.bg_opacity)
        ac.drawBackground(self.id, self.draw_bg)
        ac.drawBorder(self.id, self.draw_border)

    def show(self):
        ac.setVisible(self.id, 1)

    def hide(self):
        ac.setVisible(self.id, 0)


class UIButton(UIElement):

    def __init__(self, *args, **kwargs):
        listener = kwargs.pop('listener', None)
        super(UIElement, self).__init__(*args, **kwargs)
        self.id = ac.addButton(self.window, self.text)
        self.draw()
        if listener is not None:
            ac.addOnClickedListener(self.id, listener)


class UILabel(UIElement):

    def __init__(self, *args, **kwargs):
        super(UIElement, self).__init__(*args, **kwargs)
        self.id = ac.addLabel(self.window, self.text)
        self.draw()


class UIProgressBar(UIElement):

    def __init__(self, *args, **kwargs):
        super(UIElement, self).__init__(*args, **kwargs)
        self.id = ac.addProgressBar(self.window, self.text)
        self.draw()
