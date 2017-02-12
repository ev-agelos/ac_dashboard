"""Main dashboard that shows the car's info about speed, gears times etc."""

from itertools import cycle
import ac
from utils import int_to_time
from ui_elements import (UIProgressBar, UILabel, UIButton, Led, RedLed, GreenLed,
                         BlueLed)


class DashBoard:

    def __init__(self):
        self.data_queue = []
        self.ui_items = {}

    def notify(self, **data):
        """Add to the data list the data that got received(key=value)."""
        for telemetry, value in data.items():
            self.data_queue.append({telemetry: value})

    def subscribe(self, telemetry, element):
        """Add the ui element to the telemetry's list."""
        self.ui_items.setdefault(telemetry, []).append(element)

    def unsubscribe(self, telemetry, element):
        """Remove the ui element from the telemetry's list."""
        self.ui_items[telemetry].remove(element)

    def update(self):
        """Update every ui element depending on it's telemetry subscriptions."""
        for data in self.data_queue:
            (telemetry, value), = data.items()
            for ui_item in self.ui_items.get(telemetry, []):
                ui_item.run(telemetry, value)
        self.data_queue = []


class Speedometer:

    def __init__(self, dashboard):
        self.dashboard = dashboard
        for telemetry in ('in_pits', 'rpm'):
            self.dashboard.subscribe(telemetry, self)
        self.f1_style = False
        self.leds = {
            'green': [GreenLed(pos_x=Led.pos_x + (number*20))
                      for number in range(5)],
            'red':  [RedLed(pos_x=Led.pos_x + (number*20))
                     for number in range(5, 10)],
            'blue': [BlueLed(pos_x=Led.pos_x + (number*20))
                     for number in range(10, 15)]
        }
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


class FuelButton(UIButton):

    modes = cycle(['fuel_percent', 'burned_fuel', 'fuel_laps_left'])

    def __init__(self, dashboard):
        super().__init__(fuel_click, text='/', size=(78, 19), pos=(181, 106),
                         font_color=(0, 0, 0, 1), draw_border=1, bg_opacity=0)
        self.dashboard = dashboard
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            self.dashboard.unsubscribe(self.mode, self)
        self.mode = next(self.modes)
        self.dashboard.subscribe(self.mode, self)

    def run(self, telemetry, value):
        if telemetry == 'burned_fuel':
            text = '{0:.1f}L'.format(value)
            self.text = 'Pre: ' + text
        elif telemetry == 'fuel_laps_left':
            self.text = 'Laps: {}'.format(value)
        elif telemetry == 'fuel_percent':
            self.text = str(round(value, 1)) + '%'


class GearLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(288, 55), size=(40, 55), bg_opacity=0,
                         font_color=(1, 0, 0, 1), font_size=40)
        self.dashboard = dashboard
        self.dashboard.subscribe('gear', self)

    def run(self, telemetry, value):
        self.text = str(value)


class SpeedRpmButton(UIButton):

    modes = cycle(['speed', 'max_speed', 'rpm'])

    def __init__(self, dashboard):
        super().__init__(rpm_speed_click, pos=(355, 67), size=(80, 35),
                         font_color=(1, 0, 0, 1), font_size=25)
        self.dashboard = dashboard
        self.dashboard.subscribe('in_pits', self)
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            self.dashboard.unsubscribe(self.mode, self)
        self.mode = next(self.modes)
        self.dashboard.subscribe(self.mode, self)

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
                self.text = 'IN PITS'
                self.font_color = (1, 0, 0, 1)
            else:
                self.dashboard.subscribe(self.mode, self)
            self.lock = value


class TimesButton(UIButton):

    modes = cycle(['pb', 'theoretical_best'])

    def __init__(self, dashboard):
        super().__init__(times_click, pos=(268, 105), size=(80, 20),
                         font_size=15)
        self.dashboard = dashboard
        self.dashboard.subscribe('in_pits', self)
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            self.dashboard.unsubscribe(self.mode, self)
        self.mode = next(self.modes)
        self.dashboard.subscribe(self.mode, self)

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


class PosLapsButton(UIButton):

    modes = cycle(['laps', 'position'])

    def __init__(self, dashboard):
        super().__init__(pos_laps_click, text='/', pos=(180, 67),
                         size=(80, 33), text_align='left', font_size=25)
        self.dashboard = dashboard
        self.dashboard.subscribe('in_pits', self)
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            self.dashboard.unsubscribe(self.mode, self)
        self.mode = next(self.modes)
        self.dashboard.subscribe(self.mode, self)

    def run(self, telemetry, value):
        if telemetry == 'laps':
            text = " L: {total_laps}/{laps_counter}"
            self.text = text.format(**value)
        elif telemetry == 'position':
            text = " P: {car_position}/{total_cars}"
            self.text = text.format(**value)
        elif telemetry == 'in_pits':
            if value is True:
                self.dashboard.unsubscribe(self.mode, self)
            else:
                self.dashboard.subscribe(self.mode, self)
            self.lock = value


class SectorButton(UIButton):

    modes = cycle(['performance_meter', 'last_sector'])

    def __init__(self, dashboard, *args):
        super().__init__(sector_click, *args, pos=(355, 105), size=(80, 20),
                         font_size=15)
        self.dashboard = dashboard
        self.dashboard.subscribe('in_pits', self)
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            self.dashboard.unsubscribe(self.mode, self)
        self.mode = next(self.modes)
        self.dashboard.subscribe(self.mode, self)

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
        SECTOR_BUTTON.switch_mode()


def fuel_click(x, y):
    if not FUEL_BUTTON.lock:
        FUEL_BUTTON.switch_mode()


def times_click(x, y):
    if not TIMES_BUTTON.lock:
        TIMES_BUTTON.switch_mode()


def rpm_speed_click(x, y):
    if not SPEED_RPM_BUTTON.lock:
        SPEED_RPM_BUTTON.switch_mode()


def pos_laps_click(x, y):
    if not POS_LAPS_BUTTON.lock:
        POS_LAPS_BUTTON.switch_mode()


DASHBOARD = DashBoard()
FUEL_BAR = FuelBar(DASHBOARD)
FUEL_BUTTON = FuelButton(DASHBOARD)
GEAR_LABEL = GearLabel(DASHBOARD)
SPEED_RPM_BUTTON = SpeedRpmButton(DASHBOARD)
TIMES_BUTTON = TimesButton(DASHBOARD)
POS_LAPS_BUTTON = PosLapsButton(DASHBOARD)
SECTOR_BUTTON = SectorButton(DASHBOARD)
SPEEDOMETER = Speedometer(DASHBOARD)
