"""Car related information."""

from electronics import CAR_DATA


class Car:
    tc_levels = tuple()
    abs_levels = tuple()

    def __init__(self):
        self.name = ''
        self.rpm = 0
        self.max_rpm = 0
        self._speed = 0
        self.max_speed = 0
        self.g_forces = (0, 0)
        self.gear = 0
        self.fuel = 0
        self.max_fuel = 0
        self.lap_starting_fuel = 0
        self._tc = 0.0
        self.tc_level = None
        self._abs = 0.0
        self.abs_level = None
        self.drs = 0
        self.pit_limiter = 0
        self.pit_limiter_flag = False
        self.tyre_compound = ""

    @property
    def speed(self):
        """Return current speed of the car."""
        return self._speed

    @speed.setter
    def speed(self, value):
        """Save current and max speed of the car."""
        self._speed = value
        if value > self.max_speed:
            self.max_speed = round(value, 1)

    @property
    def tc(self):
        """Return car's raw traction control value."""
        return self._tc

    @tc.setter
    def tc(self, value):
        """Set the raw traction control value and map it to a level."""
        self._tc = value
        if not self.tc_levels:
            self.tc_levels = CAR_DATA.get(self.name, {}).get('tc')
            # no data for the car or has not any tc values
            if self.tc_levels is None:
                self.tc_levels = (0, )
        try:
            self.tc_level = self.tc_levels.index(round(value, 2))
        except ValueError:
            self.tc_level = 0

    @property
    def abs(self):
        """Return car's raw abs value."""
        return self._abs

    @abs.setter
    def abs(self, value):
        """Set the raw abs value and map it to a level."""
        self._abs = value
        if not self.abs_levels:
            self.abs_levels = CAR_DATA.get(self.name, {}).get('abs')
            # unknown car or has not any abs values
            if self.abs_levels is None:
                self.abs_levels = (0, )
        try:
            self.abs_level = self.abs_levels.index(round(value, 2))
        except ValueError:
            self.abs_level = 0

    def get_fuel_laps_left(self):
        """Return how many laps are left according to the burned fuel."""
        return round(self.fuel // self.get_fuel_burned())

    def get_fuel_burned(self):
        """
        Return how many litres the car burned.

        The starting reference point is the <self.lap_starting_fuel> which
        should be reset after every lap to car's current fuel(<self.fuel>).
        """
        return self.lap_starting_fuel - self.fuel
