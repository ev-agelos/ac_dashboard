"""Main dashboard that shows the car's info about speed, gears times etc."""

from itertools import cycle

import ac

from convert_time import int_to_time
from ui_elements import UIProgressBar, UILabel, UIButton


class DashBoard:

    def __init__(self):
        self.data_queue = []
        self.ui_items = {}

    def notify(self, **data):
        """Add to the data list the data that got received(key=value)."""
        self.data_queue.append(data)

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


class FuelBar(UIProgressBar):

    def __init__(self, window, dashboard):
        super().__init__(
            window, size=(65, 17), pos=(181, 105), font_color=(1, 0.56, 0, 1),
            bg_color=(1, 1, 0), draw_bg=1, draw_border=0)

        self.dashboard = dashboard
        self.pit_limiter_flag = None
        for telemetry in ('max_fuel', 'fuel', 'pit_limiter',
                          'pit_limiter_flag'):
            self.dashboard.subscribe(telemetry, self)

    def run(self, telemetry, value):
        """Update the labels with the given value."""
        if telemetry == 'max_fuel':
            ac.setRange(self.id, 0, value)
            self.dashboard.unsubscribe(telemetry, self)
        elif telemetry == 'fuel':
            ac.setValue(self.id, round(value))
        elif telemetry == 'pit_limiter':
            if value > 0:
                self.hide()
            elif value == 0 and self.pit_limiter_flag is True:
                self.show()
        elif telemetry == 'pit_limiter_flag':
            self.pit_limiter_flag = value


class FuelLabel(UILabel):

    modes = cycle([
        ('max_fuel', 'fuel'),
        ('burned_fuel', ),
        ('fuel_laps_left', )
    ])

    def __init__(self, window, dashboard):
        super().__init__(window, text='/', pos=(183, 103),
                                      font_color=(0, 0, 0, 1))
        self.dashboard = dashboard
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            for telemetry in self.mode:
                self.dashboard.unsubscribe(telemetry, self)
        self.mode = next(self.modes)
        for telemetry in self.mode:
            self.dashboard.subscribe(telemetry, self)

    def run(self, telemetry, value):
        if telemetry == 'burned_fuel':
            text = '{0:.1f}L'.format(value) if value is not None else ''
            ac.setText(self.id, 'Pre: ' + text)
        elif telemetry == 'fuel_laps_left':
            ac.setText(self.id, 'Laps: {}'.format(value))
        elif telemetry == 'fuel':
            _, max_fuel = ac.getText(self.id).split('/')
            ac.setText(self.id, '{}/{}L'.format(round(value), max_fuel))
        elif telemetry == 'max_fuel':
            fuel, _ = ac.getText(self.id).split('/')
            ac.setText(self.id, '{}/{}L'.format(fuel, round(value)))


class GearLabel(UILabel):

    def __init__(self, window, dashboard):
        super().__init__(window, pos=(290, 58),
                                      font_color=(1, 0, 0, 1), font_size=40)
        self.dashboard = dashboard
        self.dashboard.subscribe('gear', self)

    def run(self, telemetry, value):
        ac.setText(self.id, str(value))


class SpeedRpmButton(UIButton):

    modes = cycle([
        ('speed', ),
        ('max_speed', ),
        ('rpm', )
    ])

    def __init__(self, window, dashboard, listener=None):
        super().__init__(window, pos=(365, 70), size=(80, 30),
                                       font_size=25, listener=listener)
        self.dashboard = dashboard
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            for telemetry in self.mode:
                self.dashboard.unsubscribe(telemetry, self)
        self.mode = next(self.modes)
        for telemetry in self.mode:
            self.dashboard.subscribe(telemetry, self)

    def run(self, telemetry, value):
        if telemetry == 'max_speed':
            ac.setFontColor(self.id, 0.5, 0, 1, 1)
        elif telemetry == 'rpm':
            ac.setFontColor(self.id, 1, 0, 0, 1)
        ac.setText(self.id, str(round(value)))


class TimesButton(UIButton):

    modes = cycle([
        ('pb', ),
        ('theoretical_best', )
    ])

    def __init__(self, window, dashboard, listener=None):
        super().__init__(window, pos=(270, 104), size=(80, 20),
                                       font_size=15, listener=listener)
        self.dashboard = dashboard
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            for telemetry in self.mode:
                self.dashboard.unsubscribe(telemetry, self)
        self.mode = next(self.modes)
        for telemetry in self.mode:
            self.dashboard.subscribe(telemetry, self)

    def run(self, telemetry, value):
        if telemetry == 'pb':
            colors = (1, 0, 0, 1)
        elif telemetry == 'theoretical_best':
            colors = (0.5, 0, 1, 1)
        ac.setText(self.id, str(int_to_time(value)))
        ac.setFontColor(self.id, *colors)


class PosLapsButton(UIButton):

    modes = cycle([
        ('total_laps', 'laps_counter'),
        ('position', 'num_cars')
    ])

    def __init__(self, window, dashboard, listener=None):
        super().__init__(window, text='/', pos=(163, 70),
                                       size=(80, 30), font_size=25,
                                       listener=listener)
        self.dashboard = dashboard
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            for telemetry in self.mode:
                self.dashboard.unsubscribe(telemetry, self)
        self.mode = next(self.modes)
        for telemetry in self.mode:
            self.dashboard.subscribe(telemetry, self)

    def run(self, telemetry, value):
        if telemetry in ('total_laps', 'laps_counter'):
            prefix = 'L: '
        elif telemetry in ('position', 'num_cars'):
            prefix = 'P: '

        if telemetry == 'total_laps':
            _, laps_counter = ac.getText(self.id).split('/')
            text = str(value + 1) + '/' + laps_counter
        elif telemetry == 'laps_counter':
            total_laps, _ = ac.getText(self.id).split('/')
            text = total_laps + '/' + str(value)
        elif telemetry == 'num_cars':
            position, _ = ac.getText(self.id).split('/')
            text = position + '/' + str(value)
        elif telemetry == 'position':
            _, num_cars = ac.getText(self.id).split('/')
            text = str(value) + '/' + num_cars

        ac.setText(self.id, prefix + text)


class SectorButton(UIButton):

    modes = cycle([
        ('performance_meter', ),
        ('last_sector_time', ),
        ('sector_pb', ),
        ('sector_overall_best', ),
    ])

    def __init__(self, window, dashboard, listener=None):
        super().__init__(window, pos=(365, 104),
                                       size=(80, 20), font_size=15,
                                       listener=listener)
        self.dashboard = dashboard
        self.mode = None
        self.switch_mode()

    def switch_mode(self):
        if self.mode is not None:
            for telemetry in self.mode:
                self.dashboard.unsubscribe(telemetry, self)
        self.mode = next(self.modes)
        for telemetry in self.mode:
            self.dashboard.subscribe(telemetry, self)

    def run(self, telemetry, value):
        if telemetry == 'performace_meter':
            sector_time = str(round(value, 1))
            if value > 0:
                colors = (1, 0, 0, 1)
                sector_prefix = '+'
            else:
                sector_prefix = '-'
                colors = (0, 1, 0, 1)
            ac.setFontColor(self.id, *colors)
            ac.setText(self.id, sector_prefix + sector_time)
        elif telemetry == 'last_sector_time':
            ac.setText(self.id, str(value))
        elif telemetry == 'sector_pb':
            if value is True:
                colors = (0, 1, 0, 1)
            elif value is False:
                colors = (1, 1, 0, 1)
            ac.setFontColor(self.id, *colors)
        elif telemetry == 'sector_overall_best':
            if value is True:
                ac.setFontColor(self.id, 1, 0, 1, 1)
