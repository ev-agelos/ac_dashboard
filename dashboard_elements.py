"""Main dashboard."""

from itertools import cycle

from utils import int_to_time
from ui_elements import UIProgressBar, UILabel, UIButton
from textures import Texture


class DashboardButton(UIButton):
    """Like UIButton but (un)sub (from)to dashboard when changing mode."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = None

    def click(self):
        if self.mode is not None:
            self.dashboard.unsubscribe(self.mode, self)
        self.mode = next(self.modes)
        self.dashboard.subscribe(self.mode, self)


class Speedometer:

    def __init__(self, dashboard, f1_style=False):
        self.dashboard = dashboard
        for telemetry in ('in_pits', 'rpm', 'lap_time'):
            self.dashboard.subscribe(telemetry, self)
        self.f1_style = f1_style
        self.leds = {
            'green': [Texture(pos_x=144 + (number*20), pos_y=41, width=32,
                              height=32, color=(1, 1, 1, 1),
                              filename='LedGreen.png')
                      for number in range(5)],
            'red':  [Texture(pos_x=144 + (number*20), pos_y=41, width=32,
                             height=32, color=(1, 1, 1, 1),
                             filename='LedRed.png')
                     for number in range(5, 10)],
            'blue': [Texture(pos_x=144 + (number*20), pos_y=41, width=32,
                             height=32, color=(1, 1, 1, 1),
                             filename='LedBlue.png')
                     for number in range(10, 15)]
        }
        self.pit_leds = Texture(pos_x=129, pos_y=67, width=343, height=38,
                                color=(1, 1, 1, 1), filename='LedsYellow.png')
        self.leds_counter = len([led for group in self.leds.values()
                                 for led in group])
        self.lock = False

    def run(self, telemetry, value):
        if telemetry == 'rpm':
            rpm = value['current']
            max_rpm = value['max']
            if self.lock or rpm > max_rpm:
                self._draw_all()
            elif rpm < 10:  # no need to render really low rpms
                pass
            else:
                self._draw(rpm, max_rpm)
        elif telemetry == 'in_pits':
            self.lock = value
        elif telemetry == 'lap_time' and self.lock:  # car is in pits
            if 500 < int(str(value)[-3:]) < 999:  # sort of blinking text
                self.pit_leds.draw()

    def _draw_all(self):
        for color_group in self.leds.values():
            for led in color_group:
                led.draw()


    def _draw(self, rpm, max_rpm):
        if self.f1_style:
            for i in range(0, round(rpm * 3 / max_rpm)):
                if i == 0:
                    for led in self.leds['green']:
                        led.draw()
                elif i == 1 and rpm > 4500:
                    for led in self.leds['red']:
                        led.draw()
                elif i == 2 and rpm > 6300:
                    for led in self.leds['blue']:
                        led.draw()
        else:
            for i in range(0, round(rpm * self.leds_counter / max_rpm)):
                if i < 5:
                    color = 'green'
                    led_index = i
                elif i < 10:
                    color = 'red'
                    led_index = i - 5
                else:
                    color = 'blue'
                    led_index = i -10
                self.leds[color][led_index].draw()


class FuelBar(UIProgressBar):

    def __init__(self, dashboard, *args):
        super().__init__(*args, size=(78, 19), pos=(181, 106),
                         font_color=(1, 0.56, 0, 1), bg_color=(1, 1, 0),
                         bg_opacity=0.4, draw_border=0)
        self.dashboard = dashboard
        self.dashboard.subscribe('fuel_percent', self)

    def run(self, telemetry, value):
        """Update the labels with the given value."""
        self.percent = value  # only update fuel_percent


class FuelButton(DashboardButton):

    modes = cycle(['fuel_percent', 'burned_fuel', 'fuel_laps_left'])

    def __init__(self, dashboard):
        super().__init__(fuel_click, text='/', size=(78, 19), pos=(181, 106),
                         font_color=(0, 0, 0, 1), draw_border=1, bg_opacity=0)
        self.dashboard = dashboard
        self.click()

    def run(self, telemetry, value):
        if telemetry =='fuel_percent':
            text = '{}%'.format(round(value, 1))
        elif telemetry == 'burned_fuel':
            text = 'Pre: {0:.1f}L'.format(value)
        else:
            text = 'Laps: {}'.format(value)
        self.text = text


class GearLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(288, 55), size=(40, 55), bg_opacity=0,
                         font_color=(1, 0, 0, 1), font_size=40)
        self.dashboard = dashboard
        self.dashboard.subscribe('gear', self)

    def run(self, telemetry, value):
        self.text = str(value)


class SpeedRpmButton(DashboardButton):

    modes = cycle(['speed', 'max_speed', 'rpm'])

    def __init__(self, dashboard):
        super().__init__(rpm_speed_click, pos=(355, 67), size=(80, 35),
                         font_color=(1, 0, 0, 1), font_size=25)
        self.dashboard = dashboard
        for telemetry in ('in_pits', 'lap_time'):
            self.dashboard.subscribe(telemetry, self)
        self.click()

    def run(self, telemetry, value):
        if telemetry == 'max_speed':
            self.font_color = (0.5, 0, 1, 1)
            self.text = str(round(value))
        elif telemetry == 'speed':
            self.font_color = (1, 0, 0, 1)
            self.text = str(round(value))
        elif telemetry == 'rpm':
            self.font_color = (1, 0, 0, 1)
            self.text = str(round(value['current']))
        elif telemetry == 'in_pits':
            if value is True:
                self.dashboard.unsubscribe(self.mode, self)
                self.mode = None
                self.text = 'IN PITS'
                self.font_color = (1, 0, 0, 1)
            else:
                while self.mode != 'speed':  # show speed when exiting pits
                    self.click()
            self.lock = value
        elif telemetry == 'lap_time' and self.lock:  # car is in pits
            if 500 < int(str(value)[-3:]) < 999:  # sort of blinking text
                self.hide_text()
            else:
                self.show_text()


class TimesButton(DashboardButton):

    modes = cycle(['pb', 'theoretical_best'])

    def __init__(self, dashboard):
        super().__init__(times_click, pos=(268, 105), size=(80, 20),
                         font_size=15)
        self.dashboard = dashboard
        self.dashboard.subscribe('in_pits', self)
        self.click()

    def run(self, telemetry, value):
        if telemetry == 'pb':
            colors = (1, 0, 0, 1)
            time = int_to_time(value) if value is not None else '--:--:--'
            self.text = str(time)
            self.font_color = colors
        elif telemetry == 'theoretical_best':
            colors = (0.5, 0, 1, 1)
            time = int_to_time(value) if value is not None else '--:--:--'
            self.text = str(time)
            self.font_color = colors
        elif telemetry == 'in_pits':
            if value is True:
                self.dashboard.unsubscribe(self.mode, self)
                self.text = '--:--:--'
            else:
                self.dashboard.subscribe(self.mode, self)
            self.lock = value


class PosLapsButton(DashboardButton):

    modes = cycle(['laps', 'position'])

    def __init__(self, dashboard):
        super().__init__(pos_laps_click, text='/', pos=(180, 67),
                         size=(80, 33), text_align='left', font_size=25)
        self.dashboard = dashboard
        for telemetry in ('in_pits', 'lap_time'):
            self.dashboard.subscribe(telemetry, self)
        self.click()

    def run(self, telemetry, value):
        if telemetry == 'laps':
            self.text = " L: {total_laps}/{laps_counter}".format(**value)
        elif telemetry == 'position':
            self.text = " P: {car_position}/{total_cars}".format(**value)
        elif telemetry == 'in_pits':
            if value is True:
                while self.mode != 'position':
                    self.click()
            self.lock = value
        elif telemetry == 'lap_time' and self.lock:  # car is in pits
            if 500 < int(str(value)[-3:]) < 999:  # sort of blinking text
                self.hide_text()
            else:
                self.show_text()


class SectorButton(DashboardButton):

    modes = cycle(['performance_meter', 'last_sector'])

    def __init__(self, dashboard, *args):
        super().__init__(sector_click, *args, pos=(355, 105), size=(80, 20),
                         font_size=15)
        self.dashboard = dashboard
        self.dashboard.subscribe('in_pits', self)
        self.click()

    def run(self, telemetry, value):
        if telemetry == 'performance_meter':
            sector_time = str(round(value, 1))
            if value > 0:
                colors = (1, 0, 0, 1)
                sector_time = '+' + sector_time
            else:
                colors = (0, 1, 0, 1)
            self.font_color = colors
            self.text = sector_time
        elif telemetry == 'last_sector':
            colors = (0, 1, 0, 1) if value['is_pb'] is True else (1, 1, 0, 1)
            self.font_color = colors
            self.text = str(value['time'])
        elif telemetry == 'in_pits':
            if value is True:
                self.dashboard.unsubscribe(self.mode, self)
                self.text = '--:--:--'
            else:
                self.dashboard.subscribe(self.mode, self)
            self.lock = value


def sector_click(x, y):
    if not SECTOR_BUTTON.lock:
        SECTOR_BUTTON.click()


def fuel_click(x, y):
    if not FUEL_BUTTON.lock:
        FUEL_BUTTON.click()


def times_click(x, y):
    if not TIMES_BUTTON.lock:
        TIMES_BUTTON.click()


def rpm_speed_click(x, y):
    if not SPEED_RPM_BUTTON.lock:
        SPEED_RPM_BUTTON.click()


def pos_laps_click(x, y):
    if not POS_LAPS_BUTTON.lock:
        POS_LAPS_BUTTON.click()


def init(telemetry_provider, app_window, car):
    elements = [
        FuelBar(telemetry_provider),
        FuelButton(telemetry_provider),
        GearLabel(telemetry_provider),
        SpeedRpmButton(telemetry_provider),
        TimesButton(telemetry_provider),
        PosLapsButton(telemetry_provider),
        SectorButton(telemetry_provider),
        Speedometer(telemetry_provider, f1_style=car=='tatuusfa1'),
    ]
    for element in elements:
        element.window = app_window
