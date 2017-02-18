"""Car related information."""

import ac

from electronics import CAR_DATA


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
            self.tc_levels = CAR_DATA.get(self.name, {}).get('tc')
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
            self.abs_levels = CAR_DATA.get(self.name, {}).get('abs')
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
