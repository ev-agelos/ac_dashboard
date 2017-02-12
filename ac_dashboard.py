import ac

try:
    import os
    import sys
    import platform
    sys.path.insert(0, "apps/python/ac_dashboard/DLLs")
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
    from utils import int_to_time
    from dashboard import (DashBoard, FuelBar, FuelButton, GearLabel,
                           SpeedRpmButton, TimesButton, PosLapsButton,
                           SectorButton, SPEEDOMETER)
    from dashboard import (DASHBOARD, FUEL_BAR, FUEL_BUTTON, GEAR_LABEL,
                           SPEED_RPM_BUTTON, TIMES_BUTTON, POS_LAPS_BUTTON,
                           SECTOR_BUTTON)
except Exception as err:
    ac.log("ac_dashboard " + str(err))
import acsys


APP_WINDOW = None
STATIC_SHARED_MEMORY_IS_READ = False
NUM_CARS = 1  # at least user's CAR
DRIVER = Driver(DASHBOARD)
CAR = Car(DASHBOARD)


def acMain(ac_version):
    """Main function that is invoked by Assetto Corsa."""
    global APP_WINDOW
    APP_WINDOW = ac.newApp("")
    ac.setSize(APP_WINDOW, 600, 170)
    ac.drawBorder(APP_WINDOW, 0)
    for dashboard_element in (FUEL_BAR, FUEL_BUTTON, GEAR_LABEL,
                              SPEED_RPM_BUTTON, TIMES_BUTTON, POS_LAPS_BUTTON,
                              SECTOR_BUTTON):
        dashboard_element.window = APP_WINDOW

    DRIVER.settings.update(nationality=get_user_nationality(),
                           controller=get_controller(),
                           racing_mode=get_racing_mode(),
                           track_temp=get_track_temp())
    DRIVER.assists.update(**get_user_assists())
    CAR.name = ac.getCarName(0)
    DRIVER.settings.update(car_upgrade=CAR.upgrade)
    if CAR.name == 'tatuusfa1':
        SPEEDOMETER.f1_style = True
    app_dir = os.path.dirname(os.path.realpath(__file__))
    ac.addRenderCallback(APP_WINDOW, onFormRender)

    add_app(app_dir, render_info_app, DRIVER.settings['car_upgrade'])

    background = ac.addLabel(APP_WINDOW, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    ac.setBackgroundTexture(background, app_dir + "/Images/Dashboard.png")
    return "AC Dashboard"


def acUpdate(deltaT):
    """Read data in real time from Assetto Corsa."""
    CAR.in_pits = ac.isCarInPitlane(0)
    DRIVER.position = ac.getCarRealTimeLeaderboardPosition(0)
    completed_laps = ac.getCarState(0, acsys.CS.LapCount)
    if completed_laps > DRIVER.total_laps:
        CAR.fuel_at_start = CAR.fuel  # keep track of fuel on lap change
        DRIVER.last_splits = ac.getLastSplits(0)
        for window, tyre in zip((WINDOW_FL, WINDOW_FR, WINDOW_RL, WINDOW_RR),
                                (FL, FR, RL, RR)):
            ac.setText(window.opt_label,
                       "Opt: {}%".format(round(tyre.time_on_opt * 100 /
                                               sum(DRIVER.last_splits))))
            tyre.time_on_opt = 0
            tyre.time_on_cold = 0
            tyre.time_on_hot = 0

    DRIVER.total_laps = completed_laps
    DRIVER.lap_time = ac.getCarState(0, acsys.CS.LapTime)
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
    DASHBOARD.notify(position=dict(car_position=DRIVER.position,
                                   total_cars=NUM_CARS))


def onFormRender(deltaT):
    ac.glColor4f(1, 1, 1, 1)  # RESET COLORS
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
        while CAR.max_fuel is None or CAR.max_rpm is None:
            CAR.max_fuel = info.static.maxFuel
            CAR.max_rpm = info.static.maxRpm
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
