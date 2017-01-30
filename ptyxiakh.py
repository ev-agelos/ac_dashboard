import ac

try:
    import os
    import sys
    import platform
    sys.path.insert(0, "apps/python/ptyxiakh/DLLs")
    if platform.architecture()[0] == "64bit":
        SYSDIR = "stdlib64"
    else:
        SYSDIR = "stdlib"
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), SYSDIR))
    os.environ['PATH'] += ';.'

    import json
    from subprocess import Popen
    from ui import TyreWindow
    from sim_info import info
    from car import Car
    from tyres import get_compound_temps
    from settings import (get_user_nationality, get_controller, get_racing_mode,
                          get_user_assists, get_track_temp)
    from car_rpms import get_max_rpm, change_track_name, change_car_name
    from convert_time import int_to_time
except Exception as err:
    ac.log("PTYXIAKH " + str(err))
import acsys


APP_DIR = os.path.split(os.path.abspath(__file__))[0]
GAME_DIR = APP_DIR.split("apps\\python\\ptyxiakh")[0]
CLIENT = os.path.join(APP_DIR, "Python33", "Client.py")
PYTHON = os.path.join(APP_DIR, "Python33", "pythonw.exe")
LOG_FILE = os.path.join(APP_DIR, "ACRanking.txt")

APP_WINDOW = 0
LOG_FILE_LAP = 0
LOG_FILE_TRACK = ""
LOG_FILE_CAR = ""
LABELS_DICT = {}

STATIC_SHARED_MEMORY_IS_READ = False

NUM_CARS = 1  # at least user's car


class Tyres:

    def __init__(self):
        self.core_temp = 0
        self.cold = 0
        self.opt = 0
        self.hot = 0
        self.wear = 0

    def measure_hot_cold(self):
        if self.core_temp < get_compound_temps(Car_0.name,
                                               Car_0.tyre_compound)[0]:
            self.cold = Driver_0.current_laptime - (self.opt + self.hot)
        elif self.core_temp > get_compound_temps(Car_0.name,
                                                 Car_0.tyre_compound)[1]:
            self.hot = Driver_0.current_laptime - (self.opt + self.cold)
        else:
            self.opt = Driver_0.current_laptime - (self.hot + self.cold)


class TyreWindow:

    # FIXME how static variable opt_label is being used for all 4 tyre windows
    # and show different temps? this seems that it should have been attribute
    # per object, not static variable. Or maybe it is a label that shows
    # something that is the same for all 4 windows?
    opt_label = None
    window = None

    def __init__(self, tyre_name, render_function, starting_label_no):
        self.tyre_name = tyre_name
        self.window = ac.newApp(tyre_name)
        self.starting_label_no = starting_label_no
        ac.setSize(self.window, 100, 120)
        opt_label = ac.addLabel(self.window, "%")
        ac.setPosition(opt_label, 30, 70)
        for i in range(3):
            LABELS_DICT[self.starting_label_no + i] = ac.addLabel(self.window,
                                                                  "")
        ac.addRenderCallback(self.window, render_function)
        ac.setFontSize(self.starting_label_no, 25)
        ac.setPosition(self.starting_label_no, 35, 30)

    def draw_tyre_colors(self, temp):
        if temp < get_compound_temps(Car_0.name, Car_0.tyre_compound)[0]:
            ac.setBackgroundColor(self.window, 0, 0, 1)
        elif temp > get_compound_temps(Car_0.name, Car_0.tyre_compound)[1]:
            ac.setBackgroundColor(self.window, 1, 0, 0)
        else:
            ac.setBackgroundColor(self.window, 0, 1, 0)

        ac.setBackgroundOpacity(self.window, 0.5)
        ac.drawBorder(self.window, 0)



class Switch:

    button = None

    def __init__(self, pos_x, pos_y, size_x, size_y, font_size, function):
        self.button = ac.addButton(APP_WINDOW, "")
        ac.addOnClickedListener(self.button, function)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        self.font_size = font_size
        self.configure_button()

    def configure_button(self):
        ac.setPosition(self.button, self.pos_x, self.pos_y)
        ac.setSize(self.button, self.size_x, self.size_y)
        ac.setBackgroundOpacity(self.button, 0)
        ac.setFontColor(self.button, 1, 0, 0, 1)
        ac.setFontSize(self.button, self.font_size)
        ac.setFontAlignment(self.button, "center")


class Driver:

    def __init__(self):
        self.pb = 0
        self.temp_theoretical = {}
        self.theoretical_best = 0
        self.norm_pos = 0
        self.temp_total_laps = 0
        self.total_laps = 0
        self.current_laptime = 0
        self.temppb = 0
        self.performance_meter = 0
        self.current_sector = 0
        self.last_sector_time = 0
        self.current_sector_index = 0
        self.number_of_laps = 0
        self.settings = {}


class DashBoard:

    def __init__(self, vis_fuel):
        # TODO: introduce some kind of on/off switch attributes like:
        # .fuel_on so it will be like this dashboad.fuel_on... nicer
        self.vis_rpm_kmh = 0
        self.vis_times = 0
        self.vis_fuel = vis_fuel
        self.vis_pos_laps = 0
        self.vis_sector = 0


FL = Tyres()
FR = Tyres()
RL = Tyres()
RR = Tyres()
Driver_0 = Driver()
Car_0 = Car()
Dashboard_0 = DashBoard(2)


def switch_sector(x, y):
    if Car_0.pit_limiter == 0:
        Dashboard_0.vis_sector = int(not bool(Dashboard_0.vis_sector))


def check_switch_sector():
    if Dashboard_0.vis_sector == 0:
        try:
            # TODO: instead of .current_sector_index -> .on_track OR
            # .out_of_pits
            if Driver_0.total_laps == 0 and Driver_0.current_sector_index > 0:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                sector_text = str(int_to_time(Driver_0.last_sector_time))
                # FIXME i re-set the text ~10 lines below..?
                ac.setText(SECTOR.button, sector_text)
            elif Driver_0.current_sector_index == 0:
                if Driver_0.last_sector_time < Driver_0.temp_theoretical["S" + str(len(list(Driver_0.temp_theoretical.keys())) - 1)][1]:
                    ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                else:
                    ac.setFontColor(SECTOR.button, 1, 1, 0, 1)
            elif Driver_0.last_sector_time < Driver_0.temp_theoretical[list(Driver_0.temp_theoretical.keys())[Driver_0.current_sector_index - 1]][0]:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
            else:
                ac.setFontColor(SECTOR.button, 1, 1, 0, 1)
            sector_text = str(int_to_time(Driver_0.last_sector_time))
            ac.setText(SECTOR.button, sector_text)
        except Exception:
            if Driver_0.total_laps == 1 and Driver_0.current_sector_index == 0:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                sector_text = str(int_to_time(Driver_0.last_sector_time))
                ac.setText(SECTOR.button, sector_text)
            else:
                ac.setText(SECTOR.button, "No Sector")
    else:
        if Driver_0.total_laps == 0:
            ac.setText(SECTOR.button, "No Laps")
        else:
            sector_text = str(round(Driver_0.performance_meter, 1))
            if Driver_0.performance_meter > 0:
                ac.setFontColor(SECTOR.button, 1, 0, 0, 1)
                sector_text = '+' + sector_text
            else:
                ac.setFontColor(SECTOR.button, 0, 1, 0, 1)
            ac.setText(SECTOR.button, sector_text)


def switch_fuel(x, y):
    if Car_0.pit_limiter == 0:
        Dashboard_0.vis_fuel = {0: 1, 1: 2}.get(Dashboard_0.vis_fuel, 0)


def switch_times(x, y):
    if Car_0.pit_limiter == 0:
        Dashboard_0.vis_times = 1 if not Dashboard_0.vis_times else 0


def check_switch_times():
    if Dashboard_0.vis_times == 0:
        time = Driver_0.pb
        colors = (1, 0, 0, 1)
    else:
        time = Driver_0.theoretical_best
        colors = (0.5, 0, 1, 1)
    ac.setText(TIMES.button, "{}".format(int_to_time(time)))
    ac.setFontColor(TIMES.button, *colors)


def switch_rpm_kmh(x, y):
    if Car_0.pit_limiter == 0:
        Dashboard_0.vis_rpm_kmh = {0: 1, 1: 2}.get(Dashboard_0.vis_rpm_kmh, 0)


def check_switch_rpm_kmh():
    if Dashboard_0.vis_rpm_kmh == 1:
        ac.setText(RPM_KMH.button, "{0}".format(round(Car_0.max_speed)))
        ac.setFontColor(RPM_KMH.button, 0.5, 0, 1, 1)
    elif Dashboard_0.vis_rpm_kmh == 2:
        ac.setText(RPM_KMH.button, "{0}".format(round(Car_0.rpm)))
        ac.setFontColor(RPM_KMH.button, 1, 0, 0, 1)
    else:
        ac.setText(RPM_KMH.button, "{0}".format(round(Car_0.speed)))


def switch_pos_laps(x, y):
    if Car_0.pit_limiter == 0:
        Dashboard_0.vis_pos_laps = 1 if not Dashboard_0.vis_pos_laps else 0


def check_switch_pos_laps():
    if Dashboard_0.vis_pos_laps == 0:
        text = "L: {}/{}".format(Driver_0.total_laps + 1,
                                 Driver_0.number_of_laps)
    else:
        text = "P: {}/{}".format(POSITION, NUM_CARS)
    ac.setText(POS_LAPS.button, text)


def check_driver_pos():
    global POSITION
    POSITION = ac.getCarRealTimeLeaderboardPosition(0) + 1



def acMain(Ptyxiakh):
    """Main function that is invoked by Assetto Corsa."""
    global APP_WINDOW, NICKNAME, TRACK
    global WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR
    APP_WINDOW = ac.newApp("")
    ac.setSize(APP_WINDOW, 600, 170)
    ac.drawBorder(APP_WINDOW, 0)
    Driver_0.pb = 0
    for i in range(0, len(ac.getLastSplits(0))):
        Driver_0.temp_theoretical['S' + str(i)] = []

    check_log_file()
    Driver_0.settings.update(nationality=get_user_nationality(),
                             controller=get_controller(),
                             racing_mode=get_racing_mode(),
                             track_temp=get_track_temp())
    Driver_0.assists.update(**get_user_assists())
    TRACK = change_track_name(ac.getTrackName(0))
    upgrade, Car_0.name = change_car_name(ac.getCarName(0))
    Driver_0.settings.update(car_upgrade=upgrade)

    WINDOW_FL = TyreWindow("F_R", render_tyre_fl, 9)
    WINDOW_FR = TyreWindow("F_L", render_tyre_fr, 14)
    WINDOW_RL = TyreWindow("R_R", render_tyre_rl, 19)
    WINDOW_RR = TyreWindow("R_L", render_tyre_rr, 24)

    add_labels()
    NICKNAME = ac.getDriverName(0)
    # FIXME should get the value from sim_info static data, 99999 is bad default
    Car_0.max_rpm = get_max_rpm(ac.getCarName(0)) or 99999

    background = ac.addLabel(APP_WINDOW, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    ac.setBackgroundTexture(background, APP_DIR + "/Images/Dashboard.png")
    return "AC-Ranking"


def acUpdate(deltaT):
    """Get real time data from Assetto Corsa."""
    Driver_0.norm_pos = ac.getCarState(0, acsys.CS.NormalizedSplinePosition)
    Driver_0.temp_total_laps = ac.getCarState(0, acsys.CS.LapCount)
    Driver_0.current_laptime = ac.getCarState(0, acsys.CS.LapTime)
    Driver_0.temppb = ac.getCarState(0, acsys.CS.BestLap)
    Car_0.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    Car_0.rpm = ac.getCarState(0, acsys.CS.RPM)
    FL.core_temp, FR.core_temp, RL.core_temp, RR.core_temp = ac.getCarState(
        0, acsys.CS.CurrentTyresCoreTemp)

    read_shared_memory()
    Car_0.g_forces = ac.getCarState(0, acsys.CS.AccG)
    Car_0.gear = ac.getCarState(0, acsys.CS.Gear)
    check_ecu()
    Driver_0.performance_meter = ac.getCarState(0, acsys.CS.PerformanceMeter)
    set_dashboard_labels(Car_0.gear)

    if Driver_0.total_laps < Driver_0.temp_total_laps:
        Driver_0.total_laps = Driver_0.temp_total_laps
        search_splits(ac.getLastSplits(0))
        last_lap = sum(ac.getLastSplits(0))
        for window, tyre in zip((WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR),
                                (FL, FR, RL, RR)):
            ac.setText(window.starting_label_no,
                       "Opt: {}%".format(round((tyre.opt * 100) / last_lap, 1)))
            tyre.opt = 0
            tyre.cold = 0
            tyre.hot = 0

    if Driver_0.current_sector != Driver_0.current_sector_index:
        Driver_0.current_sector = Driver_0.current_sector_index

    if Driver_0.temppb > 0 and (Driver_0.pb == 0 or
                                Driver_0.temppb < Driver_0.pb):
        Driver_0.pb = Driver_0.temppb
        check_time(Driver_0.temppb)

    if round(FL.core_temp, 1) == round(FR.core_temp, 1) == \
            round(RL.core_temp, 1) == round(RR.core_temp, 1) == \
            Driver_0.settings['track_temp'] and \
            len(str(Car_0.fuel)) == 4 or TRACK == "Assetto Dorifto track":
        reset_values()


def set_dashboard_labels(ac_gear):
    gear_maps = {0: 'R', 1: 'N'}
    if ac_gear in gear_maps:
        gear = gear_maps[ac_gear]
    else:
        gear = ac_gear - 1
    ac.setText(LABELS_DICT[32], "{0}".format(gear))
    check_switch_rpm_kmh()
    check_driver_pos()
    check_switch_pos_laps()
    check_switch_times()
    check_switch_sector()
    if Car_0.pit_limiter > 0:
        ac.setText(RPM_KMH.button, "IN PIT")
        for button in (SECTOR.button, TIMES.button):
            ac.setText(button, "")
        ac.setText(POS_LAPS.button, "P: {0}/{1}".format(POSITION, NUM_CARS))
        Dashboard_0.vis_pos_laps = 1
        for label in FUEL_LABELS:
            ac.setVisible(label, 0)

        for button in (RPM_KMH.button, POS_LAPS.button, SECTOR.button):
            if 500 < int(str(Driver_0.current_laptime)[-3:]) < 999:
                ac.setText(button, "")
        Car_0.pit_limiter_flag = True
    else:
        if 0 < Car_0.rpm < 10:
            Car_0.rpm = 0
        elif Car_0.rpm < 0:
            Car_0.rpm = -Car_0.rpm

    if Car_0.pit_limiter == 0 and Car_0.pit_limiter_flag is True:
        for button in (RPM_KMH.button, POS_LAPS.button, SECTOR.button,
                       TIMES.button):
            ac.setVisible(button, 1)
        for label in FUEL_LABELS:
            ac.setVisible(label, 1)
        Car_0.pit_limiter_flag = False


def check_ecu():
    ac.setVisible(ECU_LABELS[0], 1 if Car_0.drs else 0)
    ac.setVisible(ECU_LABELS[1], 1 if Car_0.abs else 0)
    ac.setVisible(ECU_LABELS[2], 1 if Car_0.tc else 0)


def check_time(pb):
    global LOG_FILE_TRACK, LOG_FILE_CAR, LOG_FILE_LAP
    splits = ac.getLastSplits(0)
    while len(splits) < 3:
        splits.append(0)

    if LOG_FILE_TRACK == TRACK and LOG_FILE_CAR == Car_0.name:
        if LOG_FILE_LAP == 0 or LOG_FILE_LAP > pb:
            pass
            # Popen([PYTHON, CLIENT, NICKNAME, TRACK, Car_0.name, str(pb),
            #        str(Car_0.max_speed)] + list(map(str,splits)) +
            #        USER_ASSISTS + Driver_0.settings['nationality'] +
            #        Driver_0.settings['controller'] +
            #        Driver_0.settings['racing_mode']])
    else:
        LOG_FILE_TRACK = TRACK
        LOG_FILE_CAR = Car_0.name
        LOG_FILE_LAP = pb
        # Popen([PYTHON, CLIENT, NICKNAME, TRACK, Car_0.name, str(pb),
        #        str(Car_0.max_speed)] + list(map(str,splits)) + USER_ASSISTS +
        #        Driver_0.settings['nationality'] +
        #        Driver_0.settings['controller'] +
        #        Driver_0.settings['racing_mode'])

    with open(LOG_FILE, 'w') as fob:
        json.dump([TRACK, Car_0.name, pb], fob)


def check_log_file():
    global LOG_FILE_TRACK, LOG_FILE_CAR, LOG_FILE_LAP
    try:
        with open(LOG_FILE) as fob:
            tempdata = json.load(fob)
            LOG_FILE_TRACK = tempdata[0]
            LOG_FILE_CAR = tempdata[1]
            LOG_FILE_LAP = tempdata[2]
    except IOError:
        tempdata = ['track', 'car', 0]
        with open(LOG_FILE, 'w') as tempfile:
            json.dump(tempdata, tempfile)


def onFormRender(deltaT):
    tyre_windows = (WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR)
    tyres = (FL, FR, RL, RR)
    for window, tyre in zip(tyre_windows, tyres):
        ac.setText(window.starting_label_no,
                   "{}C".format(round(tyre.core_temp)))

    ac.glColor4f(1, 1, 1, 1)  # RESET COLORS
    draw_dashboard()


def draw_g_forces():
    ac.glColor3f(1, 1, 0)
    if Car_0.g_forces[2] > 0.05:
        ac.glQuadTextured(104, 119, 20, 20, IMAGE_ARROW_DOWN)
    elif Car_0.g_forces[2] < -0.05:
        ac.glQuadTextured(104, 119, 20, 20, IMAGE_ARROW_UP)

    if Car_0.g_forces[0] > 0.05:
        ac.glQuadTextured(132, 147, 20, 20, IMAGE_ARROW_RIGHT)
    elif Car_0.g_forces[0] < -0.05:
        ac.glQuadTextured(130, 148, 20, 20, IMAGE_ARROW_LEFT)
    ac.setText(G_FORCES[0], "{0}".format(abs(round(Car_0.g_forces[2], 1))))
    ac.setText(G_FORCES[1], "{0}".format(abs(round(Car_0.g_forces[0], 1))))


def draw_dashboard():
    if Car_0.rpm < 10:
        pass
    elif Car_0.rpm > Car_0.max_rpm or Car_0.pit_limiter > 0:
        for i in range(0, 5):
            ac.glQuadTextured(144 + (i * 20), 40, 32, 32, IMAGE_LED_GREEN)
        for i in range(5, 10):
            ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_RED)
        for i in range(10, 15):
            ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_BLUE)
    else:
        if Car_0.name == "Formula Abarth":
            for i in range(0, round(Car_0.rpm * 3 / Car_0.max_rpm)):
                if i == 0:
                    for num in range(0, 5):
                        ac.glQuadTextured(144 + (num * 20), 40, 32, 32,
                                          IMAGE_LED_GREEN)
                elif i == 1 and Car_0.rpm > 4500:
                    for num in range(5, 10):
                        ac.glQuadTextured(144 + (num * 20), 41, 32, 32,
                                          IMAGE_LED_RED)
                elif i == 2 and Car_0.rpm > 6300:
                    for num in range(10, 15):
                        ac.glQuadTextured(144 + (num * 20), 41, 32, 32,
                                          IMAGE_LED_BLUE)
        else:
            for i in range(0, round(Car_0.rpm * 15 / Car_0.max_rpm)):
                if 0 <= i < 5:
                    ac.glQuadTextured(144 + (i * 20), 40, 32, 32,
                                      IMAGE_LED_GREEN)
                elif 5 <= i < 10:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_RED)
                else:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32,
                                      IMAGE_LED_BLUE)
    if Car_0.pit_limiter > 0:
        if 500 < int(str(Driver_0.current_laptime)[-3:]) < 999:
            ac.glQuadTextured(129, 67, 343, 38, IMAGE_LEDS_YELLOW)


def search_splits(splits):
    temp_tp = 0
    if Driver_0.temp_theoretical:
        for num in range(0, len(splits)):
            Driver_0.temp_theoretical['S' + str(num)].append(splits[num])
            Driver_0.temp_theoretical['S' + str(num)] = sorted(
                Driver_0.temp_theoretical['S' + str(num)])
            temp_tp += Driver_0.temp_theoretical['S' + str(num)][0]
        if Driver_0.theoretical_best == 0 and temp_tp > 0:
            Driver_0.theoretical_best = temp_tp
        elif temp_tp < Driver_0.theoretical_best:
            Driver_0.theoretical_best = temp_tp


def render_tyre_fl(deltaT):
    WINDOW_FL.draw_tyre_colors(FL.core_temp)
    FL.measure_hot_cold()


def render_tyre_fr(deltaT):
    WINDOW_FR.draw_tyre_colors(FR.core_temp)
    FR.measure_hot_cold()


def render_tyre_rl(deltaT):
    WINDOW_RL.draw_tyre_colors(RL.core_temp)
    RL.measure_hot_cold()


def render_tyre_rr(deltaT):
    WINDOW_RR.draw_tyre_colors(RR.core_temp)
    RR.measure_hot_cold()


def add_labels():
    global FUEL_LABELS, G_FORCES, ECU_LABELS, ELECTRONIC_LABELS
    global IMAGE_ARROW_UP, IMAGE_ARROW_DOWN, IMAGE_ARROW_RIGHT, IMAGE_ARROW_LEFT
    global IMAGE_LED_RED, IMAGE_LED_GREEN, IMAGE_LED_BLUE, IMAGE_LEDS_YELLOW
    global RPM_KMH, TIMES, POS_LAPS, SECTOR
    window_info = ac.newApp("Info")
    ac.setSize(window_info, 160, 205)
    ac.addRenderCallback(window_info, render_info)

    for i in range(32, 44):
        if i == 33:
            LABELS_DICT[i] = ac.addProgressBar(APP_WINDOW, "")
            ac.setSize(LABELS_DICT[i], 65, 17)
            ac.setFontColor(LABELS_DICT[i], 1, 0.56, 0, 1)
            ac.setBackgroundColor(LABELS_DICT[i], 1, 1, 0)
            ac.drawBackground(LABELS_DICT[i], 1)
            ac.drawBorder(LABELS_DICT[i], 0)
        elif i in (35, 36, 37, 38, 39, 40):
            LABELS_DICT[i] = ac.addLabel(window_info, "")
        elif i in (41, 42, 43):
            LABELS_DICT[i] = ac.addLabel(window_info, "")
            ac.setSize(LABELS_DICT[i], 30, 30)
            ac.setBackgroundTexture(LABELS_DICT[i], APP_DIR + "/Images/on.png")
            ac.setVisible(LABELS_DICT[i], 0)
        else:  # Benzinh, Taxuthtes
            LABELS_DICT[i] = ac.addLabel(APP_WINDOW, "")

    ac.setFontColor(LABELS_DICT[32], 1, 0, 0, 1)
    ac.setFontSize(LABELS_DICT[32], 40)
    ac.setFontColor(LABELS_DICT[34], 0, 0, 0, 1)

    FUEL_LABELS = [LABELS_DICT[33], LABELS_DICT[34]]
    ELECTRONIC_LABELS = [LABELS_DICT[35], LABELS_DICT[36], LABELS_DICT[37],
                         LABELS_DICT[38]]
    G_FORCES = [LABELS_DICT[39], LABELS_DICT[40]]
    ECU_LABELS = [LABELS_DICT[41], LABELS_DICT[42], LABELS_DICT[43]]

    app_window_labels = ([LABELS_DICT[32]] + FUEL_LABELS + ELECTRONIC_LABELS +
                         G_FORCES + ECU_LABELS)
    # Dashboard Labels(Gear,RPM/Speed,Pos/Laps,
    # last_sector_time/performance_meter,LastLap)
    positions = [
        (290, 58),
        (181, 105), (183, 103),  # progressbar/Fuel,Pre,Est
        (50, 35), (10, 55), (35, 120), (35, 150),  # Tyres/Optimum temps/ABS/TC
        (133, 119), (103, 145),  # G_FORCES
        (400, 7), (3, 114), (3, 144)  # ECU Images(on)
    ]

    for label, pos in zip(app_window_labels, positions):
        ac.setPosition(label, pos[0], pos[1])

    for i in ELECTRONIC_LABELS:
        ac.setFontSize(i, 12)

    IMAGE_ARROW_UP = ac.newTexture(APP_DIR + "/Images/arrowUp.png")
    IMAGE_ARROW_DOWN = ac.newTexture(APP_DIR + "/Images/arrowDown.png")
    IMAGE_ARROW_RIGHT = ac.newTexture(APP_DIR + "/Images/arrowRight.png")
    IMAGE_ARROW_LEFT = ac.newTexture(APP_DIR + "/Images/arrowLeft.png")
    IMAGE_LED_RED = ac.newTexture(APP_DIR + "/Images/LedRed.png")
    IMAGE_LED_GREEN = ac.newTexture(APP_DIR + "/Images/LedGreen.png")
    IMAGE_LED_BLUE = ac.newTexture(APP_DIR + "/Images/LedBlue.png")
    IMAGE_LEDS_YELLOW = ac.newTexture(APP_DIR + "/Images/LedsYellow.png")
    ac.addRenderCallback(APP_WINDOW, onFormRender)

    RPM_KMH = Switch(365, 70, 80, 30, 25, switch_rpm_kmh)
    TIMES = Switch(270, 104, 80, 20, 15, switch_times)
    Fuel = Switch(181, 105, 65, 18, 15, switch_fuel)
    POS_LAPS = Switch(163, 70, 80, 30, 25, switch_pos_laps)
    SECTOR = Switch(365, 104, 80, 20, 15, switch_sector)

    # Prepei na mpei teleytaio gia na fortwnei meta to prasino eikonidio gia na
    # kratietai to diafano...
    background = ac.addLabel(window_info, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 161, 205)
    car_upgrade_img_path = os.path.join(
        APP_DIR, "/Images/Info{}.png".format(Driver_0.settings['car_upgrade']))
    ac.setBackgroundTexture(background, car_upgrade_img_path)


def render_info(deltaT):
    draw_g_forces()


def reset_values():
    Car_0.max_speed = 0
    Driver_0.total_laps = 0
    Car_0.starting_fuel = 0


def read_shared_memory():
    Car_0.tc = info.physics.tc
    tc_text = ''
    if len(Car_0.tc_levels) > 2:
        tc_text = '{}/{}'.format(Car_0.tc_level, len(Car_0.tc_levels))
    ac.setText(ELECTRONIC_LABELS[3], tc_text)

    Car_0.abs = info.physics.abs
    abs_text = ''
    if len(Car_0.abs_levels) > 2:
        abs_text = '{}/{}'.format(Car_0.abs_level, len(Car_0.abs_levels))
    ac.setText(ELECTRONIC_LABELS[2], abs_text)

    Car_0.drs = info.physics.drs
    Car_0.pit_limiter = info.physics.pitLimiterOn

    Car_0.fuel = info.physics.fuel

    if Car_0.lap_starting_fuel == 0:
        Car_0.lap_starting_fuel = Car_0.fuel
    if not STATIC_SHARED_MEMORY_IS_READ:
        read_static_shared_memory()

    update_fuel_indicator()
    FL.wear, FR.wear, RL.wear, RR.wear = list(info.physics.tyreWear)

    Car_0.tyre_compound = info.graphics.tyreCompound
    Driver_0.lastSectorTime = info.graphics.lastSectorTime
    Driver_0.current_sector_index = info.graphics.currentSectorIndex

    if Car_0.tyre_compound:
        # TODO: this should be a property for Car() and should be set when
        # .tyre_compound is set(once)
        ac.setText(ELECTRONIC_LABELS[0], Car_0.tyre_compound)
        min_temp, max_temp = get_compound_temps(Car_0.name, Car_0.tyre_compound)
        ac.setText(ELECTRONIC_LABELS[1],
                   "Optimum Temps: {}-{}C".format(min_temp, max_temp))

    Driver_0.number_of_laps = info.graphics.numberOfLaps


def read_static_shared_memory():
    global STATIC_SHARED_MEMORY_IS_READ, NUM_CARS

    Car_0.max_fuel = info.static.maxFuel
    ac.setRange(FUEL_LABELS[0], 0, Car_0.max_fuel)
    NUM_CARS = info.static.numCars

    STATIC_SHARED_MEMORY_IS_READ = True


def update_fuel_indicator():
    ac.setValue(FUEL_LABELS[0], round(Car_0.fuel))

    if Dashboard_0.vis_fuel == 0:
        if Driver_0.total_laps > 0:
            ac.setText(FUEL_LABELS[1], "Pre: {0:.1f}L".format(
                Car_0.get_fuel_burned()))
        else:
            ac.setText(FUEL_LABELS[1], "Pre: ")
    elif Dashboard_0.vis_fuel == 1:
        if Driver_0.total_laps > 0:
            ac.setText(FUEL_LABELS[1], "Laps: {0}".format(
                Car_0.get_fuel_laps_left()))
        else:
            ac.setText(FUEL_LABELS[1], "Laps: ")
    else:
        ac.setText(FUEL_LABELS[1], "{0}/{1}L".format(round(Car_0.fuel),
                                                     round(Car_0.max_fuel)))
