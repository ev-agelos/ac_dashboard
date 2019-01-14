"""Car related information."""


import json

from collections import defaultdict
from utils import int_to_time


def get_car_electronics(car):
    with open('electronics.json') as fob:
        data = json.load(fob)
    return data.get(car, {})


class TelemetryProvider:
    """Data provider to update any subscribed element."""

    registered_dashboards = []

    def __init__(self):
        self.data_queue = []
        self.ui_items = {}
        self.registered_dashboards.append(self)

    def notify(self, **telemetries):
        """Notify all registered dashboards with the telemetries received."""
        for telemetry, value in telemetries.items():
            for instance in self.registered_dashboards:
                instance.data_queue.append({telemetry: value})

    def subscribe(self, telemetry, element):
        """Add the ui element to the telemetry's list."""
        self.ui_items.setdefault(telemetry, []).append(element)

    def unsubscribe(self, telemetry, element):
        """Remove the ui element from the telemetry's list."""
        self.ui_items[telemetry].remove(element)

    def update(self):
        """Update every ui element depending on it's telemetry subscriptions."""
        for telemetry in self.data_queue:
            (telemetry_name, telemetry_value), = telemetry.items()
            for ui_item in self.ui_items.get(telemetry_name, []):
                ui_item.run(telemetry_name, telemetry_value)
        self.data_queue = []


class Car:
    """Information about car's telemetry data."""

    tc_levels = tuple()
    abs_levels = tuple()

    def __init__(self, dashboard):
        self._name = ''
        self.upgrade = ''
        self._rpm = 0
        self.max_rpm = 0
        self._speed = 0
        self.max_speed = 0
        self._g_forces = (0, 0, 0)
        self._gear = 0
        self._fuel = None
        self.max_fuel = None
        self._fuel_at_start = None
        self.burned_fuel = 0
        self.est_fuel_laps = None
        self._tc = 0.0
        self.tc_level = None
        self._abs = 0.0
        self.abs_level = None
        self.drs = 0
        self._in_pits = None
        self.electronics = {}

        self.dashboard = dashboard

    @property
    def g_forces(self):
        return self._g_forces

    @g_forces.setter
    def g_forces(self, value):
        self._g_forces = value
        self.dashboard.notify(lateral_force=self._g_forces[0],
                              transverse_force=self._g_forces[2])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        if value.endswith(('_s1', '_s2', '_s3', '_drift', '_dtm')):
            self.upgrade = value.split('_')[-1]
        self.electronics = get_car_electronics(value)

    @property
    def in_pits(self):
        return self._in_pits

    @in_pits.setter
    def in_pits(self, value):
        if bool(value) != self._in_pits:
            self._in_pits = bool(value)
            self.dashboard.notify(in_pits=self._in_pits)

    @property
    def gear(self):
        return self._gear

    @gear.setter
    def gear(self, value):
        normalized_gears = {0: 'R', 1: 'N'}
        gear = normalized_gears.get(value)
        if gear is None:
            gear = value - 1
        self._gear = gear
        self.dashboard.notify(gear=gear)

    @property
    def rpm(self):
        return self._rpm

    @rpm.setter
    def rpm(self, value):
        if 0 < value < 10:
            self._rpm = 0
        elif value < 0:
            self._rpm = -value
        else:
            self._rpm = value
        self.dashboard.notify(rpm=dict(current=self._rpm, max=self.max_rpm))

    @property
    def speed(self):
        """Return current speed of the CAR."""
        return self._speed

    @speed.setter
    def speed(self, value):
        """Save current and max speed of the CAR."""
        self._speed = value
        if value > self.max_speed:
            self.max_speed = round(value, 1)
        self.dashboard.notify(speed=value, max_speed=self.max_speed)

    @property
    def tc(self):
        """Return CAR's raw traction control value."""
        return self._tc

    @tc.setter
    def tc(self, value):
        """Set the raw traction control value and map it to a level."""
        self._tc = value
        if not self.tc_levels:
            self.tc_levels = self.electronics.get('tc')
            # no data for the CAR or has not any tc values
            if self.tc_levels is None:
                self.tc_levels = (0, )
        try:
            self.tc_level = self.tc_levels.index(round(value, 2))
        except ValueError:
            # ac.log("Ptyxiakh: Unknown TC value {} for car {}"
            #        .format(round(value, 2), self.name))
            self.tc_level = 0

        self.dashboard.notify(traction_control=dict(
            value=value, level=self.tc_level, levels=self.tc_levels))

    @property
    def abs(self):
        """Return CAR's raw abs value."""
        return self._abs

    @abs.setter
    def abs(self, value):
        """Set the raw abs value and map it to a level."""
        self._abs = value
        if not self.abs_levels:
            self.abs_levels = self.electronics.get('abs')
            # unknown CAR or has not any abs values
            if self.abs_levels is None:
                self.abs_levels = (0, )
        try:
            self.abs_level = self.abs_levels.index(round(value, 2))
        except ValueError:
            # ac.log("Ptyxiakh: Unknown ABS value {} for car {}"
            #        .format(round(value, 2), self.name))
            self.abs_level = 0

        self.dashboard.notify(abs=dict(
            value=value, level=self.abs_level, levels=self.abs_levels))

    @property
    def fuel(self):
        return self._fuel

    @fuel.setter
    def fuel(self, value):
        if value is not None:
            self._fuel = value
            if self._fuel_at_start is None and self._fuel > 0:  # set the first value
                self._fuel_at_start = self._fuel
            fuel_percent = (value * 100) / self.max_fuel
            self.dashboard.notify(fuel_percent=fuel_percent)

        self.dashboard.notify(burned_fuel=self.burned_fuel,
                              fuel_laps_left=self.est_fuel_laps)

    @property
    def fuel_at_start(self):
        return self._fuel_at_start

    @fuel_at_start.setter
    def fuel_at_start(self, value):
        self.burned_fuel = self._fuel_at_start - value
        if self.burned_fuel == 0:
            self.est_fuel_laps = 0
        else:
            self.est_fuel_laps = round(self.fuel // self.burned_fuel)
        self._fuel_at_start = value


class Driver:

    def __init__(self, dashboard):
        self._pb = None
        self._position = None
        self.last_splits = None
        self.temp_theoretical = defaultdict(list)
        self.theoretical_best = None
        self._total_laps = 0
        self._lap_time = 0
        self._performance_meter = None
        self._last_sector_time = None
        self._sector = None
        self.laps_counter = 0
        self.settings = {}

        self.dashboard = dashboard

    @property
    def lap_time(self):
        return self._lap_time

    @lap_time.setter
    def lap_time(self, value):
        self._lap_time = value
        self.dashboard.notify(lap_time=self._lap_time)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value + 1

    @property
    def sector(self):
        return self._sector

    @sector.setter
    def sector(self, value):
        if value != self._sector:
            self._sector = value

    @property
    def last_sector_time(self):
        return self._last_sector_time

    @last_sector_time.setter
    def last_sector_time(self, value):
        self._last_sector_time = int_to_time(value)

        last_sector_index = str(self.sector - 1)
        best_sector_time = min(self.temp_theoretical['S' + last_sector_index] or
                               [value + 1])
        self.dashboard.notify(last_sector=dict(time=self._last_sector_time,
                                               is_pb=value < best_sector_time))

        # save last sector time
        self.temp_theoretical['S' + last_sector_index].append(value)

    @property
    def total_laps(self):
        return self._total_laps

    @total_laps.setter
    def total_laps(self, value):
        if value > self._total_laps >= 0:
            self._total_laps = value
            # calc optimum time after lap completion
            self.theoretical_best = self.get_theoretical_best()
        self.dashboard.notify(theoretical_best=self.theoretical_best)
        self.dashboard.notify(laps=dict(total_laps=value,
                                        laps_counter=self.laps_counter))

    @property
    def pb(self):
        return self._pb

    @pb.setter
    def pb(self, value):
        self._pb = value
        self.dashboard.notify(pb=value)

    @property
    def performance_meter(self):
        return self._performance_meter

    @performance_meter.setter
    def performance_meter(self, value):
        self._performance_meter = value
        self.dashboard.notify(performance_meter=value)

    def get_theoretical_best(self):
        for num, split in enumerate(self.last_splits):
            self.temp_theoretical['S' + str(num)].append(split)
        optimum = sum([min(split_list)
                       for _, split_list in self.temp_theoretical.items()])
        return optimum
