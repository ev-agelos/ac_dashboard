import ac

try:
    import os
    import sys
    import platform
    import threading
    sys.path.insert(0, "apps/python/ac_dashboard/DLLs")
    SYSDIR = "stdlib64" if platform.architecture()[0] == "64bit" else "stdlib"
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), SYSDIR))
    os.environ['PATH'] += ';.'

    from sim_info import info
    import info_app
    from models import TelemetryProvider, Car, Driver
    import dashboard_elements
    import tyre_apps
except Exception as err:
    ac.log("ac_dashboard: " + str(err))
import acsys


MAIN_APP_TELEMETRY = TelemetryProvider()
DRIVER = Driver(MAIN_APP_TELEMETRY)
CAR = Car(MAIN_APP_TELEMETRY)


def read_static_shared_memory():
    global NUM_CARS
    while not (info.static.maxFuel or info.static.maxRpm or info.static.numCars):
        continue  # wait for both to be read
    CAR.max_fuel = info.static.maxFuel
    CAR.max_rpm = info.static.maxRpm
    NUM_CARS = info.static.numCars


def acMain(ac_version):
    """Main function that is invoked by Assetto Corsa."""
    global app_window
    app_window = ac.newApp("")
    ac.setSize(app_window, 343, 78)
    ac.drawBorder(app_window, 0)
    app_dir = os.path.dirname(os.path.realpath(__file__))
    ac.setBackgroundTexture(app_window, app_dir + "/Images/Dashboard.png")
    ac.addRenderCallback(app_window, render_app)

    CAR.name = ac.getCarName(0)
    dashboard_elements.init(MAIN_APP_TELEMETRY, app_window, CAR.name)

    tyre_apps.init(MAIN_APP_TELEMETRY)
    info_app.init()

    threading.Thread(target=read_static_shared_memory).start()

    return "AC Dashboard"


def acUpdate(delta_t):
    """Read data in real time from Assetto Corsa."""
    # ac api
    CAR.in_pits = ac.isCarInPitlane(0)
    CAR.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    CAR.rpm = ac.getCarState(0, acsys.CS.RPM)
    CAR.g_forces = ac.getCarState(0, acsys.CS.AccG)
    CAR.gear = ac.getCarState(0, acsys.CS.Gear)
    DRIVER.position = ac.getCarRealTimeLeaderboardPosition(0)
    DRIVER.lap_time = ac.getCarState(0, acsys.CS.LapTime)
    DRIVER.pb = ac.getCarState(0, acsys.CS.BestLap)
    DRIVER.performance_meter = ac.getCarState(0, acsys.CS.PerformanceMeter)

    # shared memory
    CAR.tc = info.physics.tc
    CAR.abs = info.physics.abs
    CAR.drs = info.physics.drs
    CAR.fuel = info.physics.fuel
    DRIVER.sector = info.graphics.currentSectorIndex
    DRIVER.laps_counter = info.graphics.numberOfLaps
    DRIVER.last_sector_time = info.graphics.lastSectorTime

    # on lap change keep track of fuel and read then last splits
    completed_laps = ac.getCarState(0, acsys.CS.LapCount)
    if completed_laps > DRIVER.total_laps:
        CAR.fuel_at_start = CAR.fuel
        DRIVER.last_splits = ac.getLastSplits(0)
        tyre_apps.set_tyre_usage(DRIVER.last_splits)
    DRIVER.total_laps = completed_laps

    tyre_apps.set_tyre_temps(*ac.getCarState(0, acsys.CS.CurrentTyresCoreTemp))
    slip_ratios = ac.getCarState(0, acsys.CS.SlipRatio)
    lateral_slips = ac.getCarState(0, acsys.CS.NdSlip)
    tyre_apps.set_tyre_slips(slip_ratios, lateral_slips)
    MAIN_APP_TELEMETRY.notify(position=dict(car_position=DRIVER.position,
                                            total_cars=NUM_CARS))
    

def render_app(delta_t):
    # NOTE: call MAIN_APP_TELEMETRY here so it can include any renderings otherwise
    # AC does not render if any renderings are called outside of the function
    # that has been registered with ac.addRenderCallback
    ac.setBackgroundOpacity(app_window, 1)
    MAIN_APP_TELEMETRY.update()




