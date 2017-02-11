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

    def __init__(self, name, tyre=None, render_function=None):
        self.window = ac.newApp(name)
        self.tyre = tyre
        ac.setSize(self.window, 100, 120)
        self.opt_label = ac.addLabel(self.window, "%")
        ac.setPosition(self.opt_label, 30, 70)
        self.starting_label_no = ac.addLabel(self.window, "")
        ac.addRenderCallback(self.window, render_function)
        ac.setFontSize(self.starting_label_no, 25)
        ac.setPosition(self.starting_label_no, 35, 30)

    def draw_tyre_colors(self, temp):
        if temp < self.tyre.low_opt:
            ac.setBackgroundColor(self.window, 0, 0, 1)
        elif temp > self.tyre.high_opt:
            ac.setBackgroundColor(self.window, 1, 0, 0)
        else:
            ac.setBackgroundColor(self.window, 0, 1, 0)

        ac.setBackgroundOpacity(self.window, 0.5)
        ac.drawBorder(self.window, 0)


def get_compound_temps(car_name, compound):
    """Return the optimum temp range of the <compound>."""
    tyre_temps = TYRE_COMPS
    if car_name == "lotus_exos_125_s1":
        tyre_temps = EXOS_TYRE_COMPS
    return tyre_temps.get(compound, (0, 0))


class Tyre:

    def __init__(self):
        self._compound = None
        self.low_opt = 0
        self.high_opt = 0
        self.time_on_cold = 0
        self.time_on_opt = 0
        self.time_on_hot = 0

    @property
    def compound(self):
        return self._compound

    @compound.setter
    def compound(self, value):
        self._compound = value
        self.low_opt, self.high_opt = TYRE_COMPS.get(self.compound, (0, 0))

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


def render_tyre_fl(deltaT):
    FR.compound = info.graphics.tyreCompound
    WINDOW_FL.draw_tyre_colors(FL.temp)


def render_tyre_fr(deltaT):
    FL.compound = info.graphics.tyreCompound
    WINDOW_FR.draw_tyre_colors(FR.temp)


def render_tyre_rl(deltaT):
    RR.compound = info.graphics.tyreCompound
    WINDOW_RL.draw_tyre_colors(RL.temp)


def render_tyre_rr(deltaT):
    RL.compound =info.graphics.tyreCompound
    WINDOW_RR.draw_tyre_colors(RR.temp)


FL = Tyre()
FR = Tyre()
RL = Tyre()
RR = Tyre()
WINDOW_FL = TyreWindow("F_L", tyre=FL, render_function=render_tyre_fl)
WINDOW_FR = TyreWindow("F_R", tyre=FR, render_function=render_tyre_fr)
WINDOW_RL = TyreWindow("R_L", tyre=RL, render_function=render_tyre_rl)
WINDOW_RR = TyreWindow("R_R", tyre=RR, render_function=render_tyre_rr)
