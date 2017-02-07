from collections import defaultdict

import ac

from convert_time import int_to_time


class Driver:

    def __init__(self, dashboard):
        self._pb = None
        self.temp_theoretical = defaultdict(list)
        self.theoretical_best = None
        self.norm_pos = 0
        self.temp_total_laps = 0
        self._total_laps = 0
        self.current_laptime = 0
        self.temppb = 0
        self._performance_meter = None
        self._last_sector_time = None
        self._sector = None
        self._laps_counter = 0
        self.settings = {}
        self.assists = {}

        self.dashboard = dashboard

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
        self.dashboard.notify(last_sector_time=self._last_sector_time)

        last_sector_index = str(self.sector - 1)
        best_sector_time = min(self.temp_theoretical['S' + last_sector_index] or [value + 1])
        self.dashboard.notify(sector_pb=value < best_sector_time)

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
        self.dashboard.notify(total_laps=value)

    @property
    def laps_counter(self):
        return self._laps_counter

    @laps_counter.setter
    def laps_counter(self, value):
        self._laps_counter = value
        self.dashboard.notify(laps_counter=value)

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
        for num, split in enumerate(ac.getLastSplits(0)):
            self.temp_theoretical['S' + str(num)].append(split)
        optimum = sum([min(split_list)
                       for _, split_list in self.temp_theoretical.items()])
        return optimum

