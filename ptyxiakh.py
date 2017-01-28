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
    import configparser
    from glob import glob
    from subprocess import *
    from sim_info import info
    from car_rpms import *
    from convert_time import *
except Exception as err:
    ac.log("PTYXIAKH " + str(err))
import acsys


APP_DIR = os.path.split(os.path.abspath(__file__))[0]
GAME_DIR = APP_DIR.split("apps\\python\\ptyxiakh")[0]
CLIENT = os.path.join(APP_DIR, "Python33", "Client.py")
PYTHON = os.path.join(APP_DIR, "Python33", "pythonw.exe")

APP_WINDOW = 0
USER_SETTINGS = []
LOG_FILE_LAP = 0
LOG_FILE_TRACK = ""
LOG_FILE_CAR = ""
LABELS_DICT = {}
######################################## AFTER OPTIMIZING ##############################
STATIC_SHARED_MEMORY_FLAG = True
#######################################################################################


class Tyres:
    def __init__(self):
        self.core_temp = 0
        self.cold = 0
        self.opt = 0
        self.hot = 0
        self.wear = 0


class TyreWindow():
    opt_label = None
    window = None

    def __init__(self, tyre_name, render_tyre, starting_label_no):
        self.tyre_name = tyre_name
        self.window = ac.newApp(tyre_name)
        self.starting_label_no = starting_label_no
        ac.setSize(self.window, 100, 120)
        opt_label = ac.addLabel(self.window, "%")
        ac.setPosition(opt_label, 30, 70)
        for i in range(3):
            LABELS_DICT[self.starting_label_no+i] = ac.addLabel(self.window, "")
        ac.addRenderCallback(self.window, render_tyre)


class Switch():
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


class Driver():
    def __init__(self):
        self.pb = 0
        self.temp_theoritical = {}
        self.theoritical_best = 0
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


class Car():
    def __init__(self):
        self.rpm = 0
        self.max_rpm = 0
        self.speed = 0
        self.maxspeed = 0
        self.g_forces = (0, 0)
        self.gear = 0
        self.starting_fuel = 0
        self.tc = 0
        self.abs = 0
        self.drs = 0
        self.pit_limiter = 0
        self.pit_limiter_flag = False
        self.fuel = 0
        self.max_fuel = 0
        self.tyre_compound = ""


class DashBoard():

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
###########################################################################################     Switches   ##########################################################


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
                ac.setText(SECTOR.button, "{0}".format(int_to_time(Driver_0.last_sector_time)))
            elif Driver_0.current_sector_index == 0:
                if Driver_0.last_sector_time < Driver_0.temp_theoritical["S" + str(len(list(Driver_0.temp_theoritical.keys())) - 1)][1]:
                    ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                else:
                    ac.setFontColor(SECTOR.button, 1, 1, 0, 1)
            elif Driver_0.last_sector_time < Driver_0.temp_theoritical[list(Driver_0.temp_theoritical.keys())[Driver_0.current_sector_index - 1]][0]:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
            else:
                ac.setFontColor(SECTOR.button, 1, 1, 0, 1)
            ac.setText(SECTOR.button, "{0}".format(int_to_time(Driver_0.last_sector_time)))
        except:
            if Driver_0.total_laps == 1 and Driver_0.current_sector_index == 0:
                ac.setFontColor(SECTOR.button, 1, 0, 1, 1)
                ac.setText(SECTOR.button, "{0}".format(int_to_time(Driver_0.last_sector_time)))
            else:
                ac.setText(SECTOR.button, "No Sector")
    else:
        if Driver_0.total_laps == 0:
            ac.setText(SECTOR.button, "No Laps")
        else:
            if Driver_0.performance_meter > 0:
                ac.setFontColor(SECTOR.button, 1, 0, 0, 1)
                ac.setText(SECTOR.button, "+{0}".format(round(Driver_0.performance_meter, 1)))
            else:
                ac.setFontColor(SECTOR.button, 0, 1, 0, 1)
                ac.setText(SECTOR.button, "{0}".format(round(Driver_0.performance_meter, 1)))


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
        time = Driver_0.theoritical_best
        colors = (0.5, 0, 1, 1)
    ac.setText(TIMES.button, "{}".format(int_to_time(time)))
    ac.setFontColor(TIMES.button, *colors)


def switch_rpm_kmh(x, y):
    if Car_0.pit_limiter == 0:
        Dashboard_0.vis_rpm_kmh = {0: 1, 1: 2}.get(Dashboard_0.vis_rpm_kmh, 0)


def check_switch_rpm_kmh():
    if Dashboard_0.vis_rpm_kmh == 1:
        ac.setText(RPM_KMH.button, "{0}".format(round(Car_0.maxspeed)))
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


def get_user_settings():
    global RACING_MODE, USER_ASSISTS, AMBIENT_TEMP
    CfgFolder = glob("C://Users//*//Documents//Assetto Corsa//cfg//")[0]
    config = configparser.ConfigParser(inline_comment_prefixes=(';'))

    config.read(CfgFolder + 'race.ini')
    tempnationality = config['CAR_0']['NATIONALITY']
    nationality = lambda x: '' if x == 'Planet Earth' else x
    AMBIENT_TEMP = float(config['TEMPERATURE']['ambient'])

    config.read(CfgFolder + 'controls.ini')
    InputController = config['HEADER']['INPUT_METHOD']

    config.read(CfgFolder + 'launcher.ini')
    mode = config['SAVED']['DRIVE']
    racingMode = lambda x: "Special Event" if x == 'specialevents' else 'Time Attack' if x == 'timeattack' else x.capitalize()
    RACING_MODE = racingMode(mode)
    USER_SETTINGS.extend((nationality(tempnationality), InputController,
                          RACING_MODE))

    config.read(CfgFolder + 'assists.ini')
    help = config['ASSISTS']
    USER_ASSISTS = ["Off" if help[i] == "0" else help[i]
                    if i in ("stability_control", "damage", "fuel_rate",
                             "tyre_wear") else "On"
                    for i in help]


def acMain(Ptyxiakh):
    global APP_WINDOW, NICKNAME, TRACK, CAR
    APP_WINDOW = ac.newApp("")
    ac.setSize(APP_WINDOW, 600, 170)
    ac.drawBorder(APP_WINDOW, 0)
    Driver_0.pb = 0
    for i in range(0, len(ac.getLastSplits(0))):
        Driver_0.temp_theoritical['S' + str(i)] = []

    check_log_file()
    get_user_settings()
    TRACK = change_track_name(ac.getTrackName(0))
    upgrade, CAR = change_car_name(ac.getCarName(0))
    USER_SETTINGS.append(upgrade)
    add_labels_2()
    add_labels()
    NICKNAME = ac.getDriverName(0)
    Car_0.max_rpm = MaxRPM(ac.getCarName(0))

    background = ac.addLabel(APP_WINDOW, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    ac.setBackgroundTexture(background, APP_DIR + "/Images/Dashboard.png")
    return "AC-Ranking"


def acUpdate(deltaT):
    Driver_0.norm_pos = ac.getCarState(0, acsys.CS.NormalizedSplinePosition)
    Driver_0.temp_total_laps = ac.getCarState(0, acsys.CS.LapCount)
    Driver_0.current_laptime = ac.getCarState(0, acsys.CS.LapTime)
    Driver_0.temppb = ac.getCarState(0, acsys.CS.BestLap)
    Car_0.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    Car_0.rpm = ac.getCarState(0, acsys.CS.RPM)
    FL.core_temp, FR.core_temp, RL.core_temp, RR.core_temp = ac.getCarState(
        0, acsys.CS.CurrentTyresCoreTemp)
    save_max_speed(Car_0.speed)
    read_shared_memory()
    Car_0.g_forces = ac.getCarState(0, acsys.CS.AccG)
    Car_0.gear = ac.getCarState(0, acsys.CS.Gear)
    check_ecu()
    Driver_0.performance_meter = ac.getCarState(0, acsys.CS.PerformanceMeter)
    set_dashboard_labels(Car_0.gear)

    if Driver_0.total_laps < Driver_0.temp_total_laps:
        Driver_0.total_laps = Driver_0.temp_total_laps
        measure_fuel_laps(Car_0.fuel)
        search_splits(ac.getLastSplits(0))
        Lastlap = sum(ac.getLastSplits(0))
        for label, tyre in zip(HOT_COLD_TYRE_LABELS, (FL, FR, RL, RR)):
            ac.setText(label,
                       "Opt: {}%".format(round((tyre.opt * 100) / Lastlap, 1)))
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
            AMBIENT_TEMP and (len(str(Car_0.fuel)) == 4 or \
                             TRACK == "Assetto Dorifto track"):
        reset_values()
###############################################################################


def set_dashboard_labels(ac_gear):
    gear_maps = {0: 'R', 1: 'N'}
    if ac_gear in gear_maps:
        gear = gear_maps[ac_gear]
    else:
        gear = ac_gear -1
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

    if Car_0.pit_limiter == 0 and Car_0.pit_limiter_flag == True:
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


def save_max_speed(speed):
    if speed > Car_0.maxspeed:
        Car_0.maxspeed = round(speed, 1)


def check_time(pb):
    global LOG_FILE_TRACK, LOG_FILE_CAR, LOG_FILE_LAP
    splits = ac.getLastSplits(0)
    while len(splits) < 3:
        splits.append(0)

    if LOG_FILE_TRACK == TRACK and LOG_FILE_CAR == CAR:
        if LOG_FILE_LAP == 0 or LOG_FILE_LAP > pb:
            pass
            #Popen([PYTHON,CLIENT,NICKNAME,TRACK,CAR,str(pb),str(Car_0.maxspeed)]+list(map(str,splits))+USER_ASSISTS+USER_SETTINGS)
    else:
        LOG_FILE_TRACK = TRACK
        LOG_FILE_CAR = CAR
        LOG_FILE_LAP = pb
        #Popen([PYTHON,CLIENT,NICKNAME,TRACK,CAR,str(pb),str(Car_0.maxspeed)]+list(map(str,splits))+USER_ASSISTS+USER_SETTINGS)

    tempdata = [TRACK, CAR, pb]
    with open(log, 'w') as tempfile:
        json.dump(tempdata, tempfile)


def check_log_file():
    global LOG_FILE_TRACK, LOG_FILE_CAR, LOG_FILE_LAP
    try:
        with open(log) as fob:
            tempdata = json.load(fob)
            LOG_FILE_TRACK = tempdata[0]
            LOG_FILE_CAR = tempdata[1]
            LOG_FILE_LAP = tempdata[2]
    except IOError:
        tempdata = ['track', 'car', 0]
        with open(log, 'w') as tempfile:
            json.dump(tempdata, tempfile)


def onFormRender(deltaT):
    for label, temp in zip(TYRE_LABELS, (FL.core_temp, FR.core_temp,
                                         RL.core_temp, RR.core_temp)):
        ac.setText(label, "{}C".format(round(temp)))

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
        if CAR == "Formula Abarth":
            for i in range(0, round(Car_0.rpm * 3 / Car_0.max_rpm)):
                if i == 0:
                    for i in range(0, 5):
                        ac.glQuadTextured(144 + (i * 20), 40, 32, 32,
                                          IMAGE_LED_GREEN)
                elif i == 1 and Car_0.rpm > 4500:
                    for i in range(5, 10):
                        ac.glQuadTextured(144 + (i * 20), 41, 32, 32,
                                          IMAGE_LED_RED)
                elif i == 2 and Car_0.rpm > 6300:
                    for i in range(10, 15):
                        ac.glQuadTextured(144 + (i * 20), 41, 32, 32,
                                          IMAGE_LED_BLUE)
        else:
            for i in range(0, round(Car_0.rpm * 15 / Car_0.max_rpm)):
                if 0 <= i < 5:
                    ac.glQuadTextured(144 +(i * 20), 40, 32, 32, IMAGE_LED_GREEN)
                elif 5 <= i < 10:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_RED)
                else:
                    ac.glQuadTextured(144 + (i * 20), 41, 32, 32, IMAGE_LED_BLUE)
    if Car_0.pit_limiter > 0:
        if 500 < int(str(Driver_0.current_laptime)[-3:]) < 999:
            ac.glQuadTextured(129, 67, 343, 38, IMAGE_LEDS_YELLOW)


def search_splits(splits):
    temptp = 0
    if Driver_0.temp_theoritical:
        for i in range(0, len(splits)):
            Driver_0.temp_theoritical['S' + str(i)].append(splits[i])
            Driver_0.temp_theoritical['S' + str(i)] = sorted(
                Driver_0.temp_theoritical['S' + str(i)])
            temptp += Driver_0.temp_theoritical['S'+ str(i)][0]
        if Driver_0.theoritical_best == 0 and temptp > 0:
            Driver_0.theoritical_best = temptp
        elif temptp < Driver_0.theoritical_best:
            Driver_0.theoritical_best = temptp


def render_tyre_fl(deltaT):
    draw_tyre_colors(FL.core_temp, WINDOW_FL.window)
    measure_hot_cold(FL.core_temp, FL)


def render_tyre_fr(deltaT):
    draw_tyre_colors(FR.core_temp, WINDOW_FR.window)
    measure_hot_cold(FR.core_temp, FR)


def render_tyre_rl(deltaT):
    draw_tyre_colors(RL.core_temp, WINDOW_RL.window)
    measure_hot_cold(RL.core_temp, RL)


def render_tyre_rr(deltaT):
    draw_tyre_colors(RR.core_temp, WINDOW_RR.window)
    measure_hot_cold(RR.core_temp, RR)


def draw_tyre_colors(temp, window):
    if temp < TYRE_COMPS[Car_0.tyre_compound][0]:
        ac.setBackgroundColor(window, 0, 0, 1)
    elif temp > TYRE_COMPS[Car_0.tyre_compound][1]:
        ac.setBackgroundColor(window, 1, 0, 0)
    else:
        ac.setBackgroundColor(window, 0, 1, 0)

    ac.setBackgroundOpacity(window, 0.5)
    ac.drawBorder(window, 0)


def measure_hot_cold(temp, tyre):
    if temp < TYRE_COMPS[Car_0.tyre_compound][0]:
        tyre.cold = Driver_0.current_laptime - (tyre.opt + tyre.hot)
    elif temp > TYRE_COMPS[Car_0.tyre_compound][1]:
        tyre.hot = Driver_0.current_laptime - (tyre.opt + tyre.cold)
    else:
        tyre.opt = Driver_0.current_laptime - (tyre.hot + tyre.cold)


def add_labels_2():
    global WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR, TYRE_LABELS
    global HOT_COLD_TYRE_LABELS
    WINDOW_FL = TyreWindow("F_R", render_tyre_fl, 9)
    WINDOW_FR = TyreWindow("F_L", render_tyre_fr, 14)
    WINDOW_RL = TyreWindow("R_R", render_tyre_rl, 19)
    WINDOW_RR = TyreWindow("R_L", render_tyre_rr, 24)
    HOT_COLD_TYRE_LABELS = [WINDOW_FL.opt_label, WINDOW_FR.opt_label,
                            WINDOW_RL.opt_label, WINDOW_RR.opt_label]
    TYRE_LABELS = [LABELS_DICT[9], LABELS_DICT[14], LABELS_DICT[19],
                   LABELS_DICT[24]]
    for label in TYRE_LABELS:
        ac.setFontSize(label, 25)
        ac.setPosition(label, 35, 30)


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
        else:                                                   #Benzinh,Taxuthtes
            LABELS_DICT[i] = ac.addLabel(APP_WINDOW, "")

    ac.setFontColor(LABELS_DICT[32], 1, 0, 0, 1)
    ac.setFontSize(LABELS_DICT[32], 40)
    ac.setFontColor(LABELS_DICT[34], 0, 0, 0, 1)

    FUEL_LABELS = [LABELS_DICT[33], LABELS_DICT[34]]
    ELECTRONIC_LABELS = [LABELS_DICT[35], LABELS_DICT[36], LABELS_DICT[37],
                         LABELS_DICT[38]]
    G_FORCES = [LABELS_DICT[39], LABELS_DICT[40]]
    ECU_LABELS = [LABELS_DICT[41], LABELS_DICT[42], LABELS_DICT[43]]
#------------------------------------------------------
    appWindowLabels = ([LABELS_DICT[32]] + FUEL_LABELS + ELECTRONIC_LABELS +
                       G_FORCES+ECU_LABELS)
    positions = [(290, 58),  # Dashboard Labels(Gear,RPM/Speed,Pos/Laps,last_sector_time/performance_meter,LastLap)
                 (181, 105), (183, 103),  # progressbar/Fuel,Pre,Est
                 (50, 35), (10, 55), (35, 120), (35, 150), # Tyres/Optimum temps/ABS/TC
                 (133, 119), (103, 145),  # G_FORCES
                 (400, 7), (3, 114), (3, 144)]  # ECU Images(on)

    for label, pos in zip(appWindowLabels, positions):
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

    background = ac.addLabel(window_info, "") # Prepei na mpei teleytaio gia na fortwnei meta to prasino eikonidio gia na kratietai to diafano...
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 161, 205)
    ac.setBackgroundTexture(background, (APP_DIR + "/Images/Info" +
                                         USER_SETTINGS[-1] + ".png"))
###########################################################################################     Info   ##########################################################


def render_info(deltaT):
    draw_g_forces()
###########################################################################################     RESET   ##########################################################


def reset_values():
    Car_0.maxspeed = 0
    Driver_0.total_laps = 0
    Car_0.starting_fuel = 0

###########################################################################################     SHARED MEMORY   ##########################################################


def read_shared_memory():
    Car_0.tc = info.physics.tc
    Car_0.abs = info.physics.abs
    Car_0.drs = info.physics.drs
    Car_0.pit_limiter = info.physics.pitLimiterOn
    check_tc_abs(round(Car_0.tc, 2), round(Car_0.abs, 2), Car_0.drs)

    Car_0.fuel = info.physics.fuel

    if Car_0.starting_fuel == 0:
        Car_0.starting_fuel = Car_0.fuel
    if STATIC_SHARED_MEMORY_FLAG == True:
        read_static_shared_memory()

    fuel_indicator(Car_0.fuel, Car_0.max_fuel)
    FL.wear, FR.wear, RL.wear, RR.wear = list(info.physics.tyreWear)

    Car_0.tyre_compound = info.graphics.tyreCompound
    Driver_0.lastSectorTime = info.graphics.lastSectorTime
    Driver_0.current_sector_index = info.graphics.currentSectorIndex

    if Car_0.tyre_compound:
        set_compound(Car_0.tyre_compound)

    Driver_0.number_of_laps = info.graphics.numberOfLaps


def read_static_shared_memory():
    global STATIC_SHARED_MEMORY_FLAG, NUM_CARS

    Car_0.max_fuel = info.static.maxFuel
    ac.setRange(FUEL_LABELS[0], 0, Car_0.max_fuel)
    NUM_CARS = info.static.numCars

    STATIC_SHARED_MEMORY_FLAG = False


def check_tc_abs(tc, abs_, drs):
    values = {
        '500 EsseEsse': (1, 1),
        '1M': (1, 1),
        'M3 E30 Sport Evolution': (0, 1),
        'M3 E30 Group A': (0, 1),
        'M3 E92': (1, 1),
        'M3 GT2': (1, 0),
        'Z4 E89 35is': (1, 1),
        'Z4 GT3': ((0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20,
                    0.21, 0.22), 1),
        '312T': (0, 0),
        '458 Italia': ((0.10, 0.14, 0.18, 0.24), 1),
        '599xx EVO': ((0.10, 0.11, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.24),
                      1),
        'F40': (0, 0),
        'X-Bow R': (0, 1),
        '2-Eleven': ((0.13, 0.20, 0.27), 1),
        'Type 49': (0, 0),
        'Elise SC': ((0.11, 0.17), 1),
        'Evora S': ((0.13, 0.20, 0.27), 1),
        'Evora GTC': ((0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.16, 0.18, 0.20,
                       0.22, 0.24), 1),
        'Evora GTE': ((0.13, 0.20, 0.27), 1),
        'Evora GX': (0, 0),
        'Exige 240': ((0.13, 0.2, 0.27), 1),
        'Exige S Roadster': ((0.13, 0.20, 0.27), 1),
        'Exige Scura': ((0.13, 0.20, 0.27), 1),
        'Exos 125': ((0.05, 0.1, 0.15, 0.2, 0.25), 0),
        'MP4-12C': ((0.16, 0.30), 1),
        'MP4-12C GT3': ((0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19,
                         0.08, 0.09, 0.10), 1),
        'P45 Competizione': (1, 1),
        'Huayra': ((0.12, 0.17, 0.22, 0.4), 1),
        'Zonda R': ((0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.16, 0.18, 0.20,
                     0.22, 0.24),
                    (0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.16, 0.18, 0.20,
                     0.22, 0.24)),
        'Formula Abarth': (0, 0)
    }
    # Check if Car is a Mod to create its values from reading its file with
    # ABS/TC values inside game's folder
    # config = configparser.ConfigParser(inline_comment_prefixes=(';'))


    #ABS#
    if CAR in values:
        if isinstance(values[CAR][1], int):
            pass
        else:
            if abs_ > 0:
                ac.setText(ELECTRONIC_LABELS[2], "{}/{}".format(
                    values[CAR][1].index(abs_) + 1, len(values[CAR][1])))
            else:
                ac.setText(ELECTRONIC_LABELS[2], "")
            #TC#
        if isinstance(values[CAR][0], int):
            pass
        else:
            if tc > 0:
                ac.setText(ELECTRONIC_LABELS[3], "{}/{}".format(
                    values[CAR][0].index(tc) + 1, len(values[CAR][0])))
            else:
                ac.setText(ELECTRONIC_LABELS[3], "")
    else:
        tc_file = (GAME_DIR + "\\content\\cars\\" + ac.getCarName(0) +
                   "\\data\\traction_control.lut")
        if os.path.isfile(tc_file):
            with open(tc_file) as fob:
                TC_Values = fob.read()
            TC_Values_list = TC_Values.split()
            Car_TC_Values = tuple([float(x.split("|")[1])
                                   for x in TC_Values_list])
            values[CAR] = (Car_TC_Values, 1)
        else:
            values[CAR] = (0, 1)


def set_compound(compound):
    global TYRE_COMPS
    TYRE_COMPS={
        'Street': (75, 85),
        'Semislicks': (75, 100),
        #GT2
        'Slick SuperSoft': (90, 105), 'Slick Soft': (90, 105), 'Slick Medium': (85, 105), 'Slick Hard': (80, 100), 'Slick SuperHard': (80, 100),
        #GT3
        'Slicks Soft': (80, 110), 'Slicks Medium': (75, 105), 'Slicks Hard': (70, 100),
        'F1 1967': (50, 90),
        'Slicks Soft Gr.A': (0, 0), 'Slicks Medium gr.A': (0, 0), 'Slicks Hard gr.A': (0, 0),
        'Slicks Soft DTM90s': (0, 0), 'Slicks Medium DTM90s': (0, 0), 'Slicks Hard DTM90s': (0, 0),
        'Street90S': (0, 0),
        'Street 90s': (0, 0),
        'Trofeo Slicks': (0, 0),
        'Soft 70F1': (50, 90),
        'Hard 70F1': (50, 90),
        'Slick Exos': (90, 120),
        'TopGear Record': (0, 0)
    }
    exos_tyres = {'Slick SuperSoft': (85, 110), 'Slick Soft': (105, 125),
                  'Slick Medium': (90, 115), 'Slick Hard': (110, 135)}
    if ac.getCarName(0) == "lotus_exos_125_s1":
        TYRE_COMPS = exos_tyres

    if compound in TYRE_COMPS:
        ac.setText(ELECTRONIC_LABELS[0], "{}".format(compound))
        ac.setText(ELECTRONIC_LABELS[1], "Optimum Temps: {}-{}C".format(
            TYRE_COMPS[compound][0], TYRE_COMPS[compound][1]))
    else:
        TYRE_COMPS = {compound: (0, 0)}
        ac.setText(ELECTRONIC_LABELS[0], "Unknown tyres!")


def measure_fuel_laps(fuel):
    global LAP_FUEL, ESTIMATED_LAPS
    LAP_FUEL = Car_0.starting_fuel - fuel
    ESTIMATED_LAPS = round(fuel // LAP_FUEL)
    Car_0.starting_fuel = fuel


def fuel_indicator(fuel, max_fuel):
    ac.setValue(FUEL_LABELS[0], round(fuel))

    if Dashboard_0.vis_fuel == 0:
        if Driver_0.total_laps > 0:
            ac.setText(FUEL_LABELS[1], "Pre: {0:.1f}L".format(LAP_FUEL))
        else:
            ac.setText(FUEL_LABELS[1], "Pre: ")
    elif Dashboard_0.vis_fuel == 1:
        if Driver_0.total_laps > 0:
            ac.setText(FUEL_LABELS[1], "Laps: {0}".format(ESTIMATED_LAPS))
        else:
            ac.setText(FUEL_LABELS[1], "Laps: ")
    else:
        ac.setText(FUEL_LABELS[1], "{0}/{1}L".format(round(fuel),
                                                    round(max_fuel)))
