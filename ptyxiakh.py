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
    from collections import defaultdict
    from subprocess import Popen
    from info_app import (add_app, switch_ecu_labels, update_ecu_labels,
                          draw_lateral_g_force, draw_transverse_g_force)
    from sim_info import info
    from car import Car
    from driver import Driver
    from tyres import get_compound_temps
    from settings import (get_user_nationality, get_controller, get_racing_mode,
                          get_user_assists, get_track_temp)
    from car_rpms import get_max_rpm, change_track_name, change_car_name
    from convert_time import int_to_time
    from dashboard import (DashBoard, FuelBar, FuelLabel, GearLabel,
                           SpeedRpmButton, TimesButton, PosLapsButton,
                           SectorButton)
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
        if self.core_temp < get_compound_temps(CAR.name,
                                               CAR.tyre_compound)[0]:
            self.cold = DRIVER.current_laptime - (self.opt + self.hot)
        elif self.core_temp > get_compound_temps(CAR.name,
                                                 CAR.tyre_compound)[1]:
            self.hot = DRIVER.current_laptime - (self.opt + self.cold)
        else:
            self.opt = DRIVER.current_laptime - (self.hot + self.cold)


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
        if temp < get_compound_temps(CAR.name, CAR.tyre_compound)[0]:
            ac.setBackgroundColor(self.window, 0, 0, 1)
        elif temp > get_compound_temps(CAR.name, CAR.tyre_compound)[1]:
            ac.setBackgroundColor(self.window, 1, 0, 0)
        else:
            ac.setBackgroundColor(self.window, 0, 1, 0)

        ac.setBackgroundOpacity(self.window, 0.5)
        ac.drawBorder(self.window, 0)


class Switch:

    id = None

    def __init__(self, pos_x, pos_y, size_x, size_y, font_size, function):
        self.id = ac.addButton(APP_WINDOW, "")
        ac.addOnClickedListener(self.id, function)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y
        self.font_size = font_size
        self.configure_button()

    def configure_button(self):
        ac.setPosition(self.id, self.pos_x, self.pos_y)
        ac.setSize(self.id, self.size_x, self.size_y)
        ac.setBackgroundOpacity(self.id, 0)
        ac.setFontColor(self.id, 1, 0, 0, 1)
        ac.setFontSize(self.id, self.font_size)
        ac.setFontAlignment(self.id, "center")


FL = Tyres()
FR = Tyres()
RL = Tyres()
RR = Tyres()
DASHBOARD = DashBoard()
DRIVER = Driver(DASHBOARD)
CAR = Car(DASHBOARD)


def switch_sector(x, y):
    if CAR.pit_limiter == 0:
        SECTOR_BUTTON.switch.mode()


def switch_fuel(x, y):
    if CAR.pit_limiter == 0:
        FUEL_LABEL.switch_mode()


def switch_times(x, y):
    if CAR.pit_limiter == 0:
        TimesButton.switch_mode()


def switch_rpm_kmh(x, y):
    if CAR.pit_limiter == 0:
        SPEED_RPM_BUTTON.switch_mode()


def switch_pos_laps(x, y):
    if CAR.pit_limiter == 0:
        POS_LAPS.switch_mode()


def acMain(Ptyxiakh):
    """Main function that is invoked by Assetto Corsa."""
    global APP_WINDOW, NICKNAME, TRACK
    global WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR
    APP_WINDOW = ac.newApp("")
    ac.setSize(APP_WINDOW, 600, 170)
    ac.drawBorder(APP_WINDOW, 0)
    DRIVER.pb = 0

    check_log_file()
    DRIVER.settings.update(nationality=get_user_nationality(),
                           controller=get_controller(),
                           racing_mode=get_racing_mode(),
                           track_temp=get_track_temp())
    DRIVER.assists.update(**get_user_assists())
    TRACK = change_track_name(ac.getTrackName(0))
    upgrade, CAR.name = change_car_name(ac.getCarName(0))
    DRIVER.settings.update(car_upgrade=upgrade)

    WINDOW_FL = TyreWindow("F_R", render_tyre_fl)
    WINDOW_FR = TyreWindow("F_L", render_tyre_fr)
    WINDOW_RL = TyreWindow("R_R", render_tyre_rl)
    WINDOW_RR = TyreWindow("R_L", render_tyre_rr)

    add_labels()
    NICKNAME = ac.getDriverName(0)
    # FIXME should get the value from sim_info static data, 99999 is bad default
    CAR.max_rpm = get_max_rpm(ac.getCarName(0)) or 99999

    background = ac.addLabel(APP_WINDOW, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    ac.setBackgroundTexture(background, APP_DIR + "/Images/Dashboard.png")
    return "AC-Ranking"


def acUpdate(deltaT):
    """Get real time data from Assetto Corsa."""
    DRIVER.norm_pos = ac.getCarState(0, acsys.CS.NormalizedSplinePosition)
    DRIVER.temp_total_laps = ac.getCarState(0, acsys.CS.LapCount)
    CAR.lap = ac.getCarState(0, acsys.CS.LapCount)
    DRIVER.current_laptime = ac.getCarState(0, acsys.CS.LapTime)
    DRIVER.temppb = ac.getCarState(0, acsys.CS.BestLap)
    CAR.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    CAR.rpm = ac.getCarState(0, acsys.CS.RPM)
    FL.core_temp, FR.core_temp, RL.core_temp, RR.core_temp = ac.getCarState(
        0, acsys.CS.CurrentTyresCoreTemp)

    read_shared_memory()
    CAR.g_forces = ac.getCarState(0, acsys.CS.AccG)
    CAR.gear = ac.getCarState(0, acsys.CS.Gear)
    switch_ecu_labels(CAR.drs, CAR.abs, CAR.tc)
    DRIVER.performance_meter = ac.getCarState(0, acsys.CS.PerformanceMeter)
    set_dashboard_labels()

    if DRIVER.total_laps < DRIVER.temp_total_laps:
        DRIVER.total_laps = DRIVER.temp_total_laps
        last_lap = sum(ac.getLastSplits(0))
        for window, tyre in zip((WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR),
                                (FL, FR, RL, RR)):
            ac.setText(window.starting_label_no,
                       "Opt: {}%".format(round((tyre.opt * 100) / last_lap, 1)))
            tyre.opt = 0
            tyre.cold = 0
            tyre.hot = 0

    if DRIVER.temppb > 0 and (DRIVER.pb == 0 or
                                DRIVER.temppb < DRIVER.pb):
        DRIVER.pb = DRIVER.temppb
        check_time(DRIVER.temppb)

    if round(FL.core_temp, 1) == round(FR.core_temp, 1) == \
            round(RL.core_temp, 1) == round(RR.core_temp, 1) == \
            DRIVER.settings['track_temp'] and \
            len(str(CAR.fuel)) == 4 or TRACK == "Assetto Dorifto track":
        reset_values()


def set_dashboard_labels():
    position = ac.getCarRealTimeLeaderboardPosition(0) + 1
    DASHBOARD.notify(position=position)
    check_switch_sector()
    if CAR.pit_limiter > 0:
        ac.setText(RPM_KMH_BUTTON.id, "IN PIT")
        for button in (SECTOR_BUTTON, TIMES_BUTTON):
            ac.setText(button.id, "")
        ac.setText(POS_LAPS_BUTTON.id, "P: {0}/{1}".format(position, NUM_CARS))
        while POS_LAPS_BUTTON.mode != ('position', 'num_cars'):
            POS_LAPS_BUTTON.switch_mode()
        FUEL_LABEL.hide()

        for button in (RPM_KMH_BUTTON, POS_LAPS_BUTTON, SECTOR_BUTTON):
            if 500 < int(str(DRIVER.current_laptime)[-3:]) < 999:
                ac.setText(button.id, "")
        CAR.pit_limiter_flag = True
    else:
        if 0 < CAR.rpm < 10:
            CAR.rpm = 0
        elif CAR.rpm < 0:
            CAR.rpm = -CAR.rpm

    if CAR.pit_limiter == 0 and CAR.pit_limiter_flag is True:
        for button in (RPM_KMH_BUTTON, POS_LAPS_BUTTON, SECTOR_BUTTON,
                       TIMES_BUTTON):
            ac.setVisible(button.id, 1)
        FUEL_LABEL.show()
        CAR.pit_limiter_flag = False


def check_time(pb):
    global LOG_FILE_TRACK, LOG_FILE_CAR, LOG_FILE_LAP
    splits = ac.getLastSplits(0)
    while len(splits) < 3:
        splits.append(0)

    if LOG_FILE_TRACK == TRACK and LOG_FILE_CAR == CAR.name:
        if LOG_FILE_LAP == 0 or LOG_FILE_LAP > pb:
            pass
            # Popen([PYTHON, CLIENT, NICKNAME, TRACK, CAR.name, str(pb),
            #        str(CAR.max_speed)] + list(map(str,splits)) +
            #        USER_ASSISTS + DRIVER.settings['nationality'] +
            #        DRIVER.settings['controller'] +
            #        DRIVER.settings['racing_mode']])
    else:
        LOG_FILE_TRACK = TRACK
        LOG_FILE_CAR = CAR.name
        LOG_FILE_LAP = pb
        # Popen([PYTHON, CLIENT, NICKNAME, TRACK, CAR.name, str(pb),
        #        str(CAR.max_speed)] + list(map(str,splits)) + USER_ASSISTS +
        #        DRIVER.settings['nationality'] +
        #        DRIVER.settings['controller'] +
        #        DRIVER.settings['racing_mode'])

    with open(LOG_FILE, 'w') as fob:
        json.dump([TRACK, CAR.name, pb], fob)


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
    if CAR.g_forces[2] > 0.05:
        draw_transverse_g_force(CAR.g_forces[0])
    elif CAR.g_forces[2] < -0.05:
        draw_transverse_g_force(CAR.g_forces[0], down=False)

    if CAR.g_forces[0] > 0.05:
        draw_lateral_g_force(CAR.g_forces[2])
    elif CAR.g_forces[0] < -0.05:
        draw_lateral_g_force(CAR.g_forces[2], right=False)


def draw_dashboard():
    if CAR.rpm < 10:
        pass
    elif CAR.rpm > CAR.max_rpm or CAR.pit_limiter > 0:
        for i in range(0, 5):
            ac.glQuadTextured(144 + (i * 20), 40, 32, 32, IMAGE_LED_GREEN)
        for i in range(5, 10):
            ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_RED)
        for i in range(10, 15):
            ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_BLUE)
    else:
        if CAR.name == "Formula Abarth":
            for i in range(0, round(CAR.rpm * 3 / CAR.max_rpm)):
                if i == 0:
                    for num in range(0, 5):
                        ac.glQuadTextured(144 + (num * 20), 40, 32, 32,
                                          IMAGE_LED_GREEN)
                elif i == 1 and CAR.rpm > 4500:
                    for num in range(5, 10):
                        ac.glQuadTextured(144 + (num * 20), 41, 32, 32,
                                          IMAGE_LED_RED)
                elif i == 2 and CAR.rpm > 6300:
                    for num in range(10, 15):
                        ac.glQuadTextured(144 + (num * 20), 41, 32, 32,
                                          IMAGE_LED_BLUE)
        else:
            for i in range(0, round(CAR.rpm * 15 / CAR.max_rpm)):
                if 0 <= i < 5:
                    ac.glQuadTextured(144 + (i * 20), 40, 32, 32,
                                      IMAGE_LED_GREEN)
                elif 5 <= i < 10:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_RED)
                else:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32,
                                      IMAGE_LED_BLUE)
    if CAR.pit_limiter > 0:
        if 500 < int(str(DRIVER.current_laptime)[-3:]) < 999:
            ac.glQuadTextured(129, 67, 343, 38, IMAGE_LEDS_YELLOW)


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
    global FUEL_LABEL, SPEED_RPM_BUTTON, TIMES_BUTTON, POS_LAPS_BUTTON
    global IMAGE_LED_RED, IMAGE_LED_GREEN, IMAGE_LED_BLUE, IMAGE_LEDS_YELLOW
    global RPM_KMH, TIMES

    FuelBar(APP_WINDOW, DASHBOARD)

    FUEL_LABEL = FuelLabel(APP_WINDOW, DASHBOARD)
    Switch(181, 105, 65, 18, 15, switch_fuel)
    GearLabel(APP_WINDOW, DASHBOARD)
    SPEED_RPM_BUTTON = SpeedRpmButton(APP_WINDOW, DASHBOARD,
                                      listener=switch_rpm_kmh)
    TIMES_BUTTON = TimesButton(APP_WINDOW, DASHBOARD, listener=switch_times)
    POS_LAPS_BUTTON = PosLapsButton(APP_WINDOW, DASHBOARD, listener=switch_pos_laps)
    SECTOR_BUTTON = SectorButton(APP_WINDOW, DASHBOARD,
                                 listener=switch_sector)

    IMAGE_LED_RED = ac.newTexture(APP_DIR + "/Images/LedRed.png")
    IMAGE_LED_GREEN = ac.newTexture(APP_DIR + "/Images/LedGreen.png")
    IMAGE_LED_BLUE = ac.newTexture(APP_DIR + "/Images/LedBlue.png")
    IMAGE_LEDS_YELLOW = ac.newTexture(APP_DIR + "/Images/LedsYellow.png")
    ac.addRenderCallback(APP_WINDOW, onFormRender)

    add_app(APP_DIR, onFormRender, DRIVER.settings['car_upgrade'])


def reset_values():
    CAR.max_speed = 0
    DRIVER.total_laps = 0
    CAR.starting_fuel = 0


def read_shared_memory():
    CAR.tc = info.physics.tc
    CAR.abs = info.physics.abs
    CAR.drs = info.physics.drs
    CAR.pit_limiter = info.physics.pitLimiterOn
    CAR.fuel = info.physics.fuel

    if CAR.fuel_at_start == 0:
        CAR.fuel_at_start = CAR.fuel
    if not STATIC_SHARED_MEMORY_IS_READ:
        read_static_shared_memory()

    FL.wear, FR.wear, RL.wear, RR.wear = list(info.physics.tyreWear)

    CAR.tyre_compound = info.graphics.tyreCompound

    # Read data once after sector change
    sector_index = info.graphics.currentSectorIndex
    if sector_index != DRIVER.sector:
        DRIVER.sector = sector_index
        DRIVER.last_sector_time = info.graphics.lastSectorTime
        DRIVER.laps_counter = info.graphics.numberOfLaps

    update_ecu_labels(CAR)


def read_static_shared_memory():
    global STATIC_SHARED_MEMORY_IS_READ, NUM_CARS

    CAR.max_fuel = info.static.maxFuel
    NUM_CARS = info.static.numCars
    DASHBOARD.notify(num_cars=NUM_CARS)

    STATIC_SHARED_MEMORY_IS_READ = True
