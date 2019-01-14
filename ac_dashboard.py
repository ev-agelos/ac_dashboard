import ac

try:
    import os
    import sys
    import platform
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


APP_WINDOW = None
STATIC_SHARED_MEMORY_IS_READ = False
NUM_CARS = 1  # at least user's CAR
MAIN_APP_TELEMETRY = TelemetryProvider()
DRIVER = Driver(MAIN_APP_TELEMETRY)
CAR = Car(MAIN_APP_TELEMETRY)


def acMain(ac_version):
    """Main function that is invoked by Assetto Corsa."""
    global APP_WINDOW
    APP_WINDOW = ac.newApp("")
    ac.setSize(APP_WINDOW, 600, 170)
    ac.drawBorder(APP_WINDOW, 0)

    CAR.name = ac.getCarName(0)
    dashboard_elements.init(MAIN_APP_TELEMETRY, APP_WINDOW, CAR.name)

    tyre_apps.init(MAIN_APP_TELEMETRY)

    ac.addRenderCallback(APP_WINDOW, render_app)

    info_app.init()

    background = ac.addLabel(APP_WINDOW, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    app_dir = os.path.dirname(os.path.realpath(__file__))
    ac.setBackgroundTexture(background, app_dir + "/Images/Dashboard.png")
    return "AC Dashboard"


def acUpdate(delta_t):
    """Read data in real time from Assetto Corsa."""
    CAR.in_pits = ac.isCarInPitlane(0)
    DRIVER.position = ac.getCarRealTimeLeaderboardPosition(0)
    completed_laps = ac.getCarState(0, acsys.CS.LapCount)
    if completed_laps > DRIVER.total_laps:
        CAR.fuel_at_start = CAR.fuel  # keep track of fuel on lap change
        DRIVER.last_splits = ac.getLastSplits(0)
        tyre_apps.set_tyre_usage(DRIVER.last_splits)

    DRIVER.total_laps = completed_laps
    DRIVER.lap_time = ac.getCarState(0, acsys.CS.LapTime)
    DRIVER.pb = ac.getCarState(0, acsys.CS.BestLap)
    CAR.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    CAR.rpm = ac.getCarState(0, acsys.CS.RPM)

    tyre_apps.set_tyre_temps(*ac.getCarState(0, acsys.CS.CurrentTyresCoreTemp))

    read_shared_memory()
    CAR.g_forces = ac.getCarState(0, acsys.CS.AccG)
    CAR.gear = ac.getCarState(0, acsys.CS.Gear)
    DRIVER.performance_meter = ac.getCarState(0, acsys.CS.PerformanceMeter)
    MAIN_APP_TELEMETRY.notify(position=dict(car_position=DRIVER.position,
                                            total_cars=NUM_CARS))


def render_app(delta_t):
    # NOTE: call MAIN_APP_TELEMETRY here so it can include any renderings otherwise
    # AC does not render if any renderings are called outside of the function
    # that has been registered with ac.addRenderCallback
    MAIN_APP_TELEMETRY.update()


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

    # Read data once after sector change
    sector_index = info.graphics.currentSectorIndex
    if sector_index != DRIVER.sector:
        DRIVER.sector = sector_index
    DRIVER.laps_counter = info.graphics.numberOfLaps
    DRIVER.last_sector_time = info.graphics.lastSectorTime
