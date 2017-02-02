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
    from info_app import (add_app, switch_ecu_labels, update_ecu_labels,
                          draw_lateral_g_force, draw_transverse_g_force)
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

NUM_CARS = 1  # at least user's CAR


class Tyres:

    def __init__(self):
        self.core_temp = 0
        self.cold = 0
        self.opt = 0
        self.hot = 0
        self.wear = 0

    def measure_hot_cold(self):
        if self.core_temp < get_compound_temps(CAR_0.name,
                                               CAR_0.tyre_compound)[0]:
            self.cold = DRIVER_0.current_laptime - (self.opt + self.hot)
        elif self.core_temp > get_compound_temps(CAR_0.name,
                                                 CAR_0.tyre_compound)[1]:
            self.hot = DRIVER_0.current_laptime - (self.opt + self.cold)
        else:
            self.opt = DRIVER_0.current_laptime - (self.hot + self.cold)


class TyreWindow:

    window = None

    def __init__(self, tyre_name, render_function):
        self.tyre_name = tyre_name
        self.window = ac.newApp(tyre_name)
        ac.setSize(self.window, 100, 120)
        self.opt_label = ac.addLabel(self.window, "%")
        ac.setPosition(self.opt_label, 30, 70)
        self.starting_label_no = ac.addLabel(self.window, "")
        ac.addRenderCallback(self.window, render_function)
        ac.setFontSize(self.starting_label_no, 25)
        ac.setPosition(self.starting_label_no, 35, 30)

    def draw_tyre_colors(self, temp):
        if temp < get_compound_temps(CAR_0.name, CAR_0.tyre_compound)[0]:
            ac.setBackgroundColor(self.window, 0, 0, 1)
        elif temp > get_compound_temps(CAR_0.name, CAR_0.tyre_compound)[1]:
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
        self.assists = {}


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
DRIVER_0 = Driver()
CAR_0 = Car()
Dashboard_0 = DashBoard(2)


def switch_sector(x, y):
    if CAR_0.pit_limiter == 0:
        Dashboard_0.vis_sector = int(not bool(Dashboard_0.vis_sector))


def check_switch_sector():
    if Dashboard_0.vis_sector == 0:
        try:
            # TODO: instead of .current_sector_index -> .on_track OR
            # .out_of_pits
            if DRIVER_0.total_laps == 0 and DRIVER_0.current_sector_index > 0:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                sector_text = str(int_to_time(DRIVER_0.last_sector_time))
                # FIXME i re-set the text ~10 lines below..?
                ac.setText(SECTOR.button, sector_text)
            elif DRIVER_0.current_sector_index == 0:
                if DRIVER_0.last_sector_time < DRIVER_0.temp_theoretical["S" + str(len(list(DRIVER_0.temp_theoretical.keys())) - 1)][1]:
                    ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                else:
                    ac.setFontColor(SECTOR.button, 1, 1, 0, 1)
            elif DRIVER_0.last_sector_time < DRIVER_0.temp_theoretical[list(DRIVER_0.temp_theoretical.keys())[DRIVER_0.current_sector_index - 1]][0]:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
            else:
                ac.setFontColor(SECTOR.button, 1, 1, 0, 1)
            sector_text = str(int_to_time(DRIVER_0.last_sector_time))
            ac.setText(SECTOR.button, sector_text)
        except Exception:
            if DRIVER_0.total_laps == 1 and DRIVER_0.current_sector_index == 0:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                sector_text = str(int_to_time(DRIVER_0.last_sector_time))
                ac.setText(SECTOR.button, sector_text)
            else:
                ac.setText(SECTOR.button, "No Sector")
    else:
        if DRIVER_0.total_laps == 0:
            ac.setText(SECTOR.button, "No Laps")
        else:
            sector_text = str(round(DRIVER_0.performance_meter, 1))
            if DRIVER_0.performance_meter > 0:
                ac.setFontColor(SECTOR.button, 1, 0, 0, 1)
                sector_text = '+' + sector_text
            else:
                ac.setFontColor(SECTOR.button, 0, 1, 0, 1)
            ac.setText(SECTOR.button, sector_text)


def switch_fuel(x, y):
    if CAR_0.pit_limiter == 0:
        Dashboard_0.vis_fuel = {0: 1, 1: 2}.get(Dashboard_0.vis_fuel, 0)


def switch_times(x, y):
    if CAR_0.pit_limiter == 0:
        Dashboard_0.vis_times = 1 if not Dashboard_0.vis_times else 0


def check_switch_times():
    if Dashboard_0.vis_times == 0:
        time = DRIVER_0.pb
        colors = (1, 0, 0, 1)
    else:
        time = DRIVER_0.theoretical_best
        colors = (0.5, 0, 1, 1)
    ac.setText(TIMES.button, "{}".format(int_to_time(time)))
    ac.setFontColor(TIMES.button, *colors)


def switch_rpm_kmh(x, y):
    if CAR_0.pit_limiter == 0:
        Dashboard_0.vis_rpm_kmh = {0: 1, 1: 2}.get(Dashboard_0.vis_rpm_kmh, 0)


def check_switch_rpm_kmh():
    if Dashboard_0.vis_rpm_kmh == 1:
        ac.setText(RPM_KMH.button, "{0}".format(round(CAR_0.max_speed)))
        ac.setFontColor(RPM_KMH.button, 0.5, 0, 1, 1)
    elif Dashboard_0.vis_rpm_kmh == 2:
        ac.setText(RPM_KMH.button, "{0}".format(round(CAR_0.rpm)))
        ac.setFontColor(RPM_KMH.button, 1, 0, 0, 1)
    else:
        ac.setText(RPM_KMH.button, "{0}".format(round(CAR_0.speed)))


def switch_pos_laps(x, y):
    if CAR_0.pit_limiter == 0:
        Dashboard_0.vis_pos_laps = 1 if not Dashboard_0.vis_pos_laps else 0


def check_switch_pos_laps():
    if Dashboard_0.vis_pos_laps == 0:
        text = "L: {}/{}".format(DRIVER_0.total_laps + 1,
                                 DRIVER_0.number_of_laps)
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
    DRIVER_0.pb = 0
    for i in range(0, len(ac.getLastSplits(0))):
        DRIVER_0.temp_theoretical['S' + str(i)] = []

    check_log_file()
    DRIVER_0.settings.update(nationality=get_user_nationality(),
                             controller=get_controller(),
                             racing_mode=get_racing_mode(),
                             track_temp=get_track_temp())
    DRIVER_0.assists.update(**get_user_assists())
    TRACK = change_track_name(ac.getTrackName(0))
    upgrade, CAR_0.name = change_car_name(ac.getCarName(0))
    DRIVER_0.settings.update(car_upgrade=upgrade)

    WINDOW_FL = TyreWindow("F_R", render_tyre_fl)
    WINDOW_FR = TyreWindow("F_L", render_tyre_fr)
    WINDOW_RL = TyreWindow("R_R", render_tyre_rl)
    WINDOW_RR = TyreWindow("R_L", render_tyre_rr)

    add_labels()
    NICKNAME = ac.getDriverName(0)
    # FIXME should get the value from sim_info static data, 99999 is bad default
    CAR_0.max_rpm = get_max_rpm(ac.getCarName(0)) or 99999

    background = ac.addLabel(APP_WINDOW, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    ac.setBackgroundTexture(background, APP_DIR + "/Images/Dashboard.png")
    return "AC-Ranking"


def acUpdate(deltaT):
    """Get real time data from Assetto Corsa."""
    DRIVER_0.norm_pos = ac.getCarState(0, acsys.CS.NormalizedSplinePosition)
    DRIVER_0.temp_total_laps = ac.getCarState(0, acsys.CS.LapCount)
    DRIVER_0.current_laptime = ac.getCarState(0, acsys.CS.LapTime)
    DRIVER_0.temppb = ac.getCarState(0, acsys.CS.BestLap)
    CAR_0.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    CAR_0.rpm = ac.getCarState(0, acsys.CS.RPM)
    FL.core_temp, FR.core_temp, RL.core_temp, RR.core_temp = ac.getCarState(
        0, acsys.CS.CurrentTyresCoreTemp)

    read_shared_memory()
    CAR_0.g_forces = ac.getCarState(0, acsys.CS.AccG)
    CAR_0.gear = ac.getCarState(0, acsys.CS.Gear)
    switch_ecu_labels(CAR_0.drs, CAR_0.abs, CAR_0.tc)
    DRIVER_0.performance_meter = ac.getCarState(0, acsys.CS.PerformanceMeter)
    set_dashboard_labels(CAR_0.gear)

    if DRIVER_0.total_laps < DRIVER_0.temp_total_laps:
        DRIVER_0.total_laps = DRIVER_0.temp_total_laps
        search_splits(ac.getLastSplits(0))
        last_lap = sum(ac.getLastSplits(0))
        for window, tyre in zip((WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR),
                                (FL, FR, RL, RR)):
            ac.setText(window.starting_label_no,
                       "Opt: {}%".format(round((tyre.opt * 100) / last_lap, 1)))
            tyre.opt = 0
            tyre.cold = 0
            tyre.hot = 0

    if DRIVER_0.current_sector != DRIVER_0.current_sector_index:
        DRIVER_0.current_sector = DRIVER_0.current_sector_index

    if DRIVER_0.temppb > 0 and (DRIVER_0.pb == 0 or
                                DRIVER_0.temppb < DRIVER_0.pb):
        DRIVER_0.pb = DRIVER_0.temppb
        check_time(DRIVER_0.temppb)

    if round(FL.core_temp, 1) == round(FR.core_temp, 1) == \
            round(RL.core_temp, 1) == round(RR.core_temp, 1) == \
            DRIVER_0.settings['track_temp'] and \
            len(str(CAR_0.fuel)) == 4 or TRACK == "Assetto Dorifto track":
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
    if CAR_0.pit_limiter > 0:
        ac.setText(RPM_KMH.button, "IN PIT")
        for button in (SECTOR.button, TIMES.button):
            ac.setText(button, "")
        ac.setText(POS_LAPS.button, "P: {0}/{1}".format(POSITION, NUM_CARS))
        Dashboard_0.vis_pos_laps = 1
        for label in FUEL_LABELS:
            ac.setVisible(label, 0)

        for button in (RPM_KMH.button, POS_LAPS.button, SECTOR.button):
            if 500 < int(str(DRIVER_0.current_laptime)[-3:]) < 999:
                ac.setText(button, "")
        CAR_0.pit_limiter_flag = True
    else:
        if 0 < CAR_0.rpm < 10:
            CAR_0.rpm = 0
        elif CAR_0.rpm < 0:
            CAR_0.rpm = -CAR_0.rpm

    if CAR_0.pit_limiter == 0 and CAR_0.pit_limiter_flag is True:
        for button in (RPM_KMH.button, POS_LAPS.button, SECTOR.button,
                       TIMES.button):
            ac.setVisible(button, 1)
        for label in FUEL_LABELS:
            ac.setVisible(label, 1)
        CAR_0.pit_limiter_flag = False


def check_time(pb):
    global LOG_FILE_TRACK, LOG_FILE_CAR, LOG_FILE_LAP
    splits = ac.getLastSplits(0)
    while len(splits) < 3:
        splits.append(0)

    if LOG_FILE_TRACK == TRACK and LOG_FILE_CAR == CAR_0.name:
        if LOG_FILE_LAP == 0 or LOG_FILE_LAP > pb:
            pass
            # Popen([PYTHON, CLIENT, NICKNAME, TRACK, CAR_0.name, str(pb),
            #        str(CAR_0.max_speed)] + list(map(str,splits)) +
            #        USER_ASSISTS + DRIVER_0.settings['nationality'] +
            #        DRIVER_0.settings['controller'] +
            #        DRIVER_0.settings['racing_mode']])
    else:
        LOG_FILE_TRACK = TRACK
        LOG_FILE_CAR = CAR_0.name
        LOG_FILE_LAP = pb
        # Popen([PYTHON, CLIENT, NICKNAME, TRACK, CAR_0.name, str(pb),
        #        str(CAR_0.max_speed)] + list(map(str,splits)) + USER_ASSISTS +
        #        DRIVER_0.settings['nationality'] +
        #        DRIVER_0.settings['controller'] +
        #        DRIVER_0.settings['racing_mode'])

    with open(LOG_FILE, 'w') as fob:
        json.dump([TRACK, CAR_0.name, pb], fob)


def check_log_file():
    global LOG_FILE_TRACK, LOG_FILE_CAR, LOG_FILE_LAP
    try:
        with open(LOG_FILE) as fob:
            tempdata = json.load(fob)
            LOG_FILE_TRACK = tempdata[0]
            LOG_FILE_CAR = tempdata[1]
            LOG_FILE_LAP = tempdata[2]
    except IOError:
        tempdata = ['track', 'CAR', 0]
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
    if CAR_0.g_forces[2] > 0.05:
        draw_transverse_g_force(CAR_0.g_forces[0])
    elif CAR_0.g_forces[2] < -0.05:
        draw_transverse_g_force(CAR_0.g_forces[0], down=False)

    if CAR_0.g_forces[0] > 0.05:
        draw_lateral_g_force(CAR_0.g_forces[2])
    elif CAR_0.g_forces[0] < -0.05:
        draw_lateral_g_force(CAR_0.g_forces[2], right=False)


def draw_dashboard():
    if CAR_0.rpm < 10:
        pass
    elif CAR_0.rpm > CAR_0.max_rpm or CAR_0.pit_limiter > 0:
        for i in range(0, 5):
            ac.glQuadTextured(144 + (i * 20), 40, 32, 32, IMAGE_LED_GREEN)
        for i in range(5, 10):
            ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_RED)
        for i in range(10, 15):
            ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_BLUE)
    else:
        if CAR_0.name == "Formula Abarth":
            for i in range(0, round(CAR_0.rpm * 3 / CAR_0.max_rpm)):
                if i == 0:
                    for num in range(0, 5):
                        ac.glQuadTextured(144 + (num * 20), 40, 32, 32,
                                          IMAGE_LED_GREEN)
                elif i == 1 and CAR_0.rpm > 4500:
                    for num in range(5, 10):
                        ac.glQuadTextured(144 + (num * 20), 41, 32, 32,
                                          IMAGE_LED_RED)
                elif i == 2 and CAR_0.rpm > 6300:
                    for num in range(10, 15):
                        ac.glQuadTextured(144 + (num * 20), 41, 32, 32,
                                          IMAGE_LED_BLUE)
        else:
            for i in range(0, round(CAR_0.rpm * 15 / CAR_0.max_rpm)):
                if 0 <= i < 5:
                    ac.glQuadTextured(144 + (i * 20), 40, 32, 32,
                                      IMAGE_LED_GREEN)
                elif 5 <= i < 10:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_RED)
                else:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32,
                                      IMAGE_LED_BLUE)
    if CAR_0.pit_limiter > 0:
        if 500 < int(str(DRIVER_0.current_laptime)[-3:]) < 999:
            ac.glQuadTextured(129, 67, 343, 38, IMAGE_LEDS_YELLOW)


def search_splits(splits):
    temp_tp = 0
    if DRIVER_0.temp_theoretical:
        for num in range(0, len(splits)):
            DRIVER_0.temp_theoretical['S' + str(num)].append(splits[num])
            DRIVER_0.temp_theoretical['S' + str(num)] = sorted(
                DRIVER_0.temp_theoretical['S' + str(num)])
            temp_tp += DRIVER_0.temp_theoretical['S' + str(num)][0]
        if DRIVER_0.theoretical_best == 0 and temp_tp > 0:
            DRIVER_0.theoretical_best = temp_tp
        elif temp_tp < DRIVER_0.theoretical_best:
            DRIVER_0.theoretical_best = temp_tp


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
    global FUEL_LABELS
    global IMAGE_LED_RED, IMAGE_LED_GREEN, IMAGE_LED_BLUE, IMAGE_LEDS_YELLOW
    global RPM_KMH, TIMES, POS_LAPS, SECTOR

    for i in range(32, 35):
        if i == 33:
            LABELS_DICT[i] = ac.addProgressBar(APP_WINDOW, "")
            ac.setSize(LABELS_DICT[i], 65, 17)
            ac.setFontColor(LABELS_DICT[i], 1, 0.56, 0, 1)
            ac.setBackgroundColor(LABELS_DICT[i], 1, 1, 0)
            ac.drawBackground(LABELS_DICT[i], 1)
            ac.drawBorder(LABELS_DICT[i], 0)
        else:
            LABELS_DICT[i] = ac.addLabel(APP_WINDOW, "")

    ac.setFontColor(LABELS_DICT[32], 1, 0, 0, 1)
    ac.setFontSize(LABELS_DICT[32], 40)
    ac.setFontColor(LABELS_DICT[34], 0, 0, 0, 1)

    FUEL_LABELS = [LABELS_DICT[33], LABELS_DICT[34]]

    # Dashboard Labels(Gear,RPM/Speed,Pos/Laps,
    # last_sector_time/performance_meter,LastLap)
    positions = [
        (290, 58),
        (181, 105), (183, 103),  # progressbar/Fuel,Pre,Est
    ]

    for label, pos in zip(([LABELS_DICT[32]] + FUEL_LABELS), positions):
        ac.setPosition(label, pos[0], pos[1])

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
    add_app(APP_DIR, onFormRender, DRIVER_0.settings['car_upgrade'])


def reset_values():
    CAR_0.max_speed = 0
    DRIVER_0.total_laps = 0
    CAR_0.starting_fuel = 0


def read_shared_memory():
    CAR_0.tc = info.physics.tc
    CAR_0.abs = info.physics.abs

    CAR_0.drs = info.physics.drs
    CAR_0.pit_limiter = info.physics.pitLimiterOn

    CAR_0.fuel = info.physics.fuel

    if CAR_0.lap_starting_fuel == 0:
        CAR_0.lap_starting_fuel = CAR_0.fuel
    if not STATIC_SHARED_MEMORY_IS_READ:
        read_static_shared_memory()

    update_fuel_indicator()
    FL.wear, FR.wear, RL.wear, RR.wear = list(info.physics.tyreWear)

    CAR_0.tyre_compound = info.graphics.tyreCompound
    DRIVER_0.lastSectorTime = info.graphics.lastSectorTime
    DRIVER_0.current_sector_index = info.graphics.currentSectorIndex

    update_ecu_labels(CAR_0)
    DRIVER_0.number_of_laps = info.graphics.numberOfLaps


def read_static_shared_memory():
    global STATIC_SHARED_MEMORY_IS_READ, NUM_CARS

    CAR_0.max_fuel = info.static.maxFuel
    ac.setRange(FUEL_LABELS[0], 0, CAR_0.max_fuel)
    NUM_CARS = info.static.numCars

    STATIC_SHARED_MEMORY_IS_READ = True


def update_fuel_indicator():
    ac.setValue(FUEL_LABELS[0], round(CAR_0.fuel))

    if Dashboard_0.vis_fuel == 0:
        if DRIVER_0.total_laps > 0:
            ac.setText(FUEL_LABELS[1], "Pre: {0:.1f}L".format(
                CAR_0.get_fuel_burned()))
        else:
            ac.setText(FUEL_LABELS[1], "Pre: ")
    elif Dashboard_0.vis_fuel == 1:
        if DRIVER_0.total_laps > 0:
            ac.setText(FUEL_LABELS[1], "Laps: {0}".format(
                CAR_0.get_fuel_laps_left()))
        else:
            ac.setText(FUEL_LABELS[1], "Laps: ")
    else:
        ac.setText(FUEL_LABELS[1], "{0}/{1}L".format(round(CAR_0.fuel),
                                                     round(CAR_0.max_fuel)))
