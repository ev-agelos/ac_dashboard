import time

import ac
import acsys

from sim_info import info


TYRE_COMPS = {
    'Street': (75, 85),
    'Semislicks': (75, 100),
    # GT2
    'Slick SuperSoft': (90, 105),
    'Slick Soft': (90, 105),
    'Slick Medium': (85, 105),
    'Slick Hard': (80, 100),
    'Slick SuperHard': (80, 100),
    # GT3
    'Slicks Soft': (80, 110),
    'Slicks Medium': (75, 105),
    'Slicks Hard': (70, 100),
    'F1 1967': (50, 90),
    'Slicks Soft Gr.A': (0, 0),
    'Slicks Medium gr.A': (0, 0),
    'Slicks Hard gr.A': (0, 0),
    'Slicks Soft DTM90s': (0, 0),
    'Slicks Medium DTM90s': (0, 0),
    'Slicks Hard DTM90s': (0, 0),
    'Street90S': (0, 0),
    'Street 90s': (0, 0),
    'Trofeo Slicks': (0, 0),
    'Soft 70F1': (50, 90),
    'Hard 70F1': (50, 90),
    'Slick Exos': (90, 120),
    'TopGear Record': (0, 0),
    'Slick Medium (M)': (75, 90)
}
EXOS_TYRE_COMPS = {'Slick SuperSoft': (85, 110), 'Slick Soft': (105, 125),
                   'Slick Medium': (90, 115), 'Slick Hard': (110, 135)}

class TyreWindow:

    window = None
    width = 100
    height = 120

    def __init__(self, name, tyre=None, render_function=None):
        self.window = ac.newApp(name)
        self.tyre = tyre
        ac.setIconPosition(self.window, 9999999, 99999999)  # hide the icon
        ac.setSize(self.window, TyreWindow.width, TyreWindow.height)
        self.opt_label = ac.addLabel(self.window, "Opt:")
        ac.setPosition(self.opt_label, 5, 50)
        self.slip_label = ac.addLabel(self.window, "Slip:\nSkid:")
        ac.setPosition(self.slip_label, 5, 70)
        self.starting_label_no = ac.addLabel(self.window, "")
        ac.addRenderCallback(self.window, render_function)
        ac.setFontSize(self.starting_label_no, 25)
        ac.setPosition(self.starting_label_no, 35, 20)

    def draw_tyre_slip(self, tyre):
        if tyre.slip_ratio < -self.tyre.slip_ratio_limit:
            ac.setBackgroundColor(self.window, 0, 0, 1)
        elif tyre.is_sliding:
            ac.setBackgroundColor(self.window, 1, 0, 0)
        elif tyre.slip_ratio == 0.0:  # tyre in the air
            ac.setBackgroundColor(self.window, 1, 1, 1)
        else:
            ac.setBackgroundColor(self.window, 0, 0, 0)
    
    def draw_tyre_temp_colors(self, temp):
        if not (self.tyre.low_opt or self.tyre.high_opt):
            ac.setFontColor(self.starting_label_no, 1, 1, 1, 1)
            return
        if temp < self.tyre.low_opt:
            ac.setFontColor(self.starting_label_no, 0, 0, 1, 1)
        elif temp > self.tyre.high_opt:
            ac.setFontColor(self.starting_label_no, 1, 0, 0, 1)
        else:
            ac.setFontColor(self.starting_label_no, 0, 1, 0, 1)


def get_compound_temps(car_name, compound):
    """Return the optimum temp range of the <compound>."""
    tyre_temps = TYRE_COMPS
    if car_name == "lotus_exos_125_s1":
        tyre_temps = EXOS_TYRE_COMPS
    return tyre_temps.get(compound, (0, 0))


class Tyre:

    slip_ratio_limit = 0.15
    lateral_slip_limit = 1

    def __init__(self, dashboard):
        self._compound = None
        self._temp = 0
        self.lateral_slip = 0
        self.slip_ratio = 0
        self.slip_time = 0
        self.skid_time = 0
        self.currently_slipping = False
        self.currently_skidding = False
        self.start_sliding = None
        self.start_skidding = None
        self.low_opt = 0
        self.high_opt = 0
        self.time_on_cold = 0
        self.time_on_opt = 0
        self.time_on_hot = 0

        self.dashboard = dashboard

    @property
    def compound(self):
        return self._compound

    @compound.setter
    def compound(self, value):
        self._compound = value
        self.low_opt, self.high_opt = TYRE_COMPS.get(self._compound, (0, 0))
        self.dashboard.notify(compound=self._compound,
                              optimum_temps=(self.low_opt, self.high_opt))

    @property
    def is_sliding(self):
        return self.lateral_slip > Tyre.lateral_slip_limit or \
            self.slip_ratio > Tyre.slip_ratio_limit

    @property
    def is_blocked(self):
        return self.slip_ratio < -Tyre.slip_ratio_limit

    def set_slip(self, slip_ratio, lateral_slip):
        self.slip_ratio = slip_ratio
        self.lateral_slip = lateral_slip

        if self.is_sliding:
            if self.currently_slipping:
                now = time.time()
                self.slip_time += now - self.start_sliding
                self.start_sliding = now
            else:
                self.currently_slipping = True
                self.start_sliding = time.time()
        elif self.is_blocked:
            if self.currently_skidding:
                now = time.time()
                self.skid_time += now - self.start_skidding
                self.start_skidding = now
            else:
                self.currently_skidding = True
                self.start_skidding = time.time()
        else:
            self.currently_skidding = False
            self.currently_slipping = False

    @property
    def temp(self):
        return self._temp

    @temp.setter
    def temp(self, value):
        self._temp = value
        new_time = ac.getCarState(0, acsys.CS.LapTime) - (self.time_on_cold +
                                                          self.time_on_opt +
                                                          self.time_on_hot)
        if value < self.low_opt:
            self.time_on_cold += new_time
        elif self.low_opt <= value <= self.high_opt:
            self.time_on_opt += new_time
        else:
            self.time_on_hot += new_time


def render_tyres(deltaT):
    for tyre, window in zip(TYRES, WINDOWS):
        tyre.compound = info.graphics.tyreCompound
        window.draw_tyre_temp_colors(tyre.temp)
        window.draw_tyre_slip(tyre)
        # opacity looses its value when window is clicked
        ac.setBackgroundOpacity(window.window, 1)


def set_tyre_usage(last_splits):
    for window, tyre in zip(WINDOWS, TYRES):
        laptime = sum(last_splits)
        opt_time = tyre.time_on_opt * 100 / laptime
        ac.setText(window.opt_label, "Opt: {}%".format(round(opt_time)))
        tyre.time_on_opt = 0
        tyre.time_on_cold = 0
        tyre.time_on_hot = 0

        ac.setText(window.slip_label, "Slip: {}\nSkid: {}".format(
            round(tyre.slip_time, 2),
            round(tyre.skid_time, 2)
        ))
        tyre.skid_time = 0
        tyre.slip_time = 0


def set_tyre_temps(*temps):
    TYRES[0].temp, TYRES[1].temp, TYRES[2].temp, TYRES[3].temp = temps
    for window, tyre in zip(WINDOWS, TYRES):
        ac.setText(window.starting_label_no, "{}\u2103".format(round(tyre.temp)))


def set_tyre_slips(slip_ratios, lateral_slips):
    for tyre, ratio, lateral_slip in zip(TYRES, slip_ratios, lateral_slips):
        tyre.set_slip(ratio, lateral_slip)


def init(dashboard):
    global TYRES, WINDOWS
    TYRES = [
        Tyre(dashboard),
        Tyre(dashboard),
        Tyre(dashboard),
        Tyre(dashboard),
    ]
    WINDOWS = [
        TyreWindow("FL", tyre=TYRES[0], render_function=render_tyres),
        TyreWindow("FR", tyre=TYRES[1], render_function=render_tyres),
        TyreWindow("RL", tyre=TYRES[2], render_function=render_tyres),
        TyreWindow("RR", tyre=TYRES[3], render_function=render_tyres),
    ]
