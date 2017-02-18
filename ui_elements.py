import ac


class UIElement:

    white = (1, 1, 1)
    black = (0, 0, 0)
    red = (1, 0, 0)
    green = (0, 1, 0)
    blue = (0, 0, 1)
    yellow = (1, 1, 0)
    purple = (0.5, 0, 1)

    def __init__(self, text='', text_align='center', size=(20, 20), pos=(0, 0),
                 font_color=(1, 1, 1, 1), font_size=12, bg_color=(1, 1, 1),
                 draw_bg=1, bg_opacity=0.6, bg_texture='', draw_border=0,
                 visible=1):
        self.id = None
        self._window = None
        self._text = text
        self._text_align = text_align
        self._size = size
        self._position = pos
        self._font_color = font_color
        self._font_size = font_size
        self._bg_color = bg_color
        self._draw_bg = draw_bg  # 0 (transparent) or 1 (not trasparent)
        self._bg_opacity = bg_opacity  # alpha channel 0 <= float <= 1
        self._bg_texture = bg_texture
        self._draw_border = draw_border
        self._visible = visible

    @property
    def bg_texture(self):
        return self._bg_texture

    @bg_texture.setter
    def bg_texture(self, value):
        self._bg_texture = value
        if value:
            ac.setBackgroundTexture(self.id, self._bg_texture)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        ac.setVisible(self.id, self._visible)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        ac.setText(self.id, value)

    @property
    def text_align(self):
        return self._text_align

    @text_align.setter
    def text_align(self, value):
        self._text_align = value
        if value in ('left', 'center', 'right'):
            ac.setFontAlignment(self.id, value)
        else:
            ac.console("Text align <{}> is not supported.".format(value))

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        ac.setSize(self.id, *value)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        ac.setPosition(self.id, *value)

    @property
    def font_color(self):
        return self._font_color

    @font_color.setter
    def font_color(self, value):
        self._font_color = value
        ac.setFontColor(self.id, *value)

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value
        ac.setFontSize(self.id, value)

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = value
        ac.setBackgroundColor(self.id, *value)

    @property
    def bg_opacity(self):
        return self._bg_opacity

    @bg_opacity.setter
    def bg_opacity(self, value):
        self._bg_opacity = value
        ac.setBackgroundOpacity(self.id, value)

    @property
    def draw_bg(self):
        return self._draw_bg

    @draw_bg.setter
    def draw_bg(self, value):
        self._draw_bg = value
        ac.drawBackground(self.id, value)

    @property
    def draw_border(self):
        return self._draw_border

    @draw_border.setter
    def draw_border(self, value):
        self._draw_border = value
        ac.drawBorder(self.id, value)

    def _draw(self):
        """Re-set attributes to invoke their properties now."""
        for attribute in UIElement.__init__.__code__.co_names:
            if isinstance(attribute, str) and \
                    attribute not in ('id', '_window') and \
                    hasattr(self, attribute):
                setattr(self, attribute[1:], getattr(self, attribute))

    def show(self):
        ac.setVisible(self.id, 1)

    def hide(self):
        ac.setVisible(self.id, 0)


class UILabel(UIElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        self._window = value
        self.id = ac.addLabel(self._window, '')
        self._draw()


class UIProgressBar(UIElement):

    def __init__(self, *args, **kwargs):
        self._range = (0, 100)
        self._percent = None
        super().__init__(*args, **kwargs)

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        self._window = value
        self.id = ac.addProgressBar(self._window, '')
        self._draw()

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, value):
        self._range = value
        ac.setRange(self.id, *value)

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        self._percent = value/100  # need to be 0.0 <= value <= 1.0
        ac.setValue(self.id, self._percent)


class UIButton(UIElement):

    def __init__(self, listener, *args, **kwargs):
        self.listener = listener
        super().__init__(*args, **kwargs)
        self.lock = False

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        self._window = value
        self.id = ac.addButton(self._window, '')
        ac.addOnClickedListener(self.id, self.listener)
        self._draw()

    def show_text(self):
        """Show the text of the button."""
        self.text = self._text

    def hide_text(self):
        """Hide the text of the button."""
        _text = self._text  # keep original text before setting new value
        self.text = ''  # trigger the setter
        self._text = _text  # save back the original one
