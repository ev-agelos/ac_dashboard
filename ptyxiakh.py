import ac

try:
    import os
    import sys
    import platform
    sys.path.insert(0, "apps/python/ptyxiakh/DLLs")
    SYSDIR = "stdlib64" if platform.architecture()[0] == "64bit" else "stdlib"
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
    from tyres import FL, FR, RL, RR, WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR
    from settings import (get_user_nationality, get_controller, get_racing_mode,
                          get_user_assists, get_track_temp)
    from car_rpms import get_max_rpm, change_track_name, change_car_name
    from convert_time import int_to_time
    from dashboard import (DashBoard, FuelBar, FuelButton, GearLabel,
                           SpeedRpmButton, TimesButton, PosLapsButton,
                           SectorButton, SPEEDOMETER)
    from dashboard import (DASHBOARD, FUEL_BAR, FUEL_BUTTON, GEAR_LABEL,
                           SPEED_RPM_BUTTON, TIMES_BUTTON, POS_LAPS_BUTTON,
                           SECTOR_BUTTON)
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
DRIVER = Driver(DASHBOARD)
CAR = Car(DASHBOARD)


def acMain(Ptyxiakh):
    """Main function that is invoked by Assetto Corsa."""
    global APP_WINDOW, NICKNAME, TRACK
    global IMAGE_LEDS_YELLOW
    APP_WINDOW = ac.newApp("")
    ac.setSize(APP_WINDOW, 600, 170)
    ac.drawBorder(APP_WINDOW, 0)
    for dashboard_element in (FUEL_BAR, FUEL_BUTTON, GEAR_LABEL,
                              SPEED_RPM_BUTTON, TIMES_BUTTON, POS_LAPS_BUTTON,
                              SECTOR_BUTTON):
        dashboard_element.window = APP_WINDOW

    check_log_file()
    DRIVER.settings.update(nationality=get_user_nationality(),
                           controller=get_controller(),
                           racing_mode=get_racing_mode(),
                           track_temp=get_track_temp())
    DRIVER.assists.update(**get_user_assists())
    TRACK = change_track_name(ac.getTrackName(0))
    upgrade, CAR.name = change_car_name(ac.getCarName(0))
    DRIVER.settings.update(car_upgrade=upgrade)
    if CAR.name == 'Formula Abarth':
        SPEEDOMETER.f1_style = True
    IMAGE_LEDS_YELLOW = ac.newTexture(APP_DIR + "/Images/LedsYellow.png")
    ac.addRenderCallback(APP_WINDOW, onFormRender)

    add_app(APP_DIR, render_info_app, DRIVER.settings['car_upgrade'])
    NICKNAME = ac.getDriverName(0)
    # FIXME should get the value from sim_info static data, 99999 is bad default
    CAR.max_rpm = get_max_rpm(ac.getCarName(0)) or 99999

    background = ac.addLabel(APP_WINDOW, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    ac.setBackgroundTexture(background, APP_DIR + "/Images/Dashboard.png")
    return "AC-Ranking"


def acUpdate(deltaT):
    """Read data in real time from Assetto Corsa."""
    CAR.in_pits = ac.isCarInPitlane(0)
    DRIVER.position = ac.getCarRealTimeLeaderboardPosition(0)
    completed_laps = ac.getCarState(0, acsys.CS.LapCount)
    if completed_laps > DRIVER.total_laps:
        CAR.fuel_at_start = CAR.fuel  # keep track of fuel on lap change

        last_lap = sum(ac.getLastSplits(0))
        for window, tyre in zip((WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR),
                                (FL, FR, RL, RR)):
            ac.setText(window.opt_label,
                       "Opt: {}%".format(round(tyre.time_on_opt * 100 / last_lap)))
            tyre.time_on_opt = 0
            tyre.time_on_cold = 0
            tyre.time_on_hot = 0

    DRIVER.total_laps = completed_laps
    DRIVER.current_laptime = ac.getCarState(0, acsys.CS.LapTime)
    DRIVER.pb = ac.getCarState(0, acsys.CS.BestLap)
    CAR.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    CAR.rpm = ac.getCarState(0, acsys.CS.RPM)
    FR.temp, FL.temp, RR.temp, RL.temp = ac.getCarState(
        0, acsys.CS.CurrentTyresCoreTemp)
    for window, tyre in zip((WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR),
                            (FL, FR, RL, RR)):
        ac.setText(window.starting_label_no,
                   "{}C".format(round(tyre.temp)))

    read_shared_memory()
    CAR.g_forces = ac.getCarState(0, acsys.CS.AccG)
    CAR.gear = ac.getCarState(0, acsys.CS.Gear)
    switch_ecu_labels(CAR.drs, CAR.abs, CAR.tc)
    DRIVER.performance_meter = ac.getCarState(0, acsys.CS.PerformanceMeter)
    set_dashboard_labels()
    #  check_time(DRIVER.pb)
    DASHBOARD.notify(position=dict(car_position=DRIVER.position,
                                   total_cars=NUM_CARS))


def set_dashboard_labels():
    if CAR.in_pits:
        POS_LAPS_BUTTON.text = " P: {}/{}".format(DRIVER.position, NUM_CARS)
        for button in (SPEED_RPM_BUTTON, POS_LAPS_BUTTON):
            if 500 < int(str(DRIVER.current_laptime)[-3:]) < 999:
                button.hide()
            else:
                button.show()
    else:
        if 0 < CAR.rpm < 10:
            CAR.rpm = 0
        elif CAR.rpm < 0:
            CAR.rpm = -CAR.rpm


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
    ac.glColor4f(1, 1, 1, 1)  # RESET COLORS

    if CAR.in_pits:
        if 500 < int(str(DRIVER.current_laptime)[-3:]) < 999:
            ac.glQuadTextured(129, 67, 343, 38, IMAGE_LEDS_YELLOW)
    # NOTE: call DASHBOARD here so it can include any renderings otherwise
    # AC does not render if any renderings are called outside of the function
    # that has been registered with ac.addRenderCallback
    DASHBOARD.update()


def render_info_app(deltaT):
    if CAR.g_forces[2] > 0.05:
        draw_transverse_g_force(CAR.g_forces[0])
    elif CAR.g_forces[2] < -0.05:
        draw_transverse_g_force(CAR.g_forces[0], down=False)

    if CAR.g_forces[0] > 0.05:
        draw_lateral_g_force(CAR.g_forces[2])
    elif CAR.g_forces[0] < -0.05:
        draw_lateral_g_force(CAR.g_forces[2], right=False)


def read_shared_memory():
    global STATIC_SHARED_MEMORY_IS_READ, NUM_CARS
    if not STATIC_SHARED_MEMORY_IS_READ:
        while CAR.max_fuel is None:
            CAR.max_fuel = info.static.maxFuel
        NUM_CARS = info.static.numCars
        STATIC_SHARED_MEMORY_IS_READ = True

    CAR.tc = info.physics.tc
    CAR.abs = info.physics.abs
    CAR.drs = info.physics.drs
    CAR.fuel = info.physics.fuel

    update_ecu_labels(CAR, FL.compound)

    # Read data once after sector change
    sector_index = info.graphics.currentSectorIndex
    if sector_index != DRIVER.sector:
        DRIVER.sector = sector_index
    DRIVER.laps_counter = info.graphics.numberOfLaps
    DRIVER.last_sector_time = info.graphics.lastSectorTime
