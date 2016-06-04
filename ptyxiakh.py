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
    ac.log(str(err.args))
    ac.log(str(err.msg))
    ac.log(str(err.name))
    ac.log(str(err.path))
    ac.log(str(err.with_traceback))
import acsys
app_dir = os.path.split(os.path.abspath(__file__))[0]
game_dir = app_dir.split("apps\\python\\ptyxiakh")[0]
Client = os.path.join(app_dir, "Python33", "Client.py")
Python = os.path.join(app_dir, "Python33", "pythonw.exe")
log = os.path.join(app_dir, "ACRanking.txt")

appWindow = 0
UserSETTINGS = []
LogFileLap = 0
LogFileTrack = ""
LogFileCar = ""
Labels_Dict = {}
######################################## AFTER OPTIMIZING ##############################
STATICSharedMemoryFLAG = True
#######################################################################################


class Tyres:
    def __init__(self, Core_Temp, cold, opt, hot, wear):
        self.Core_Temp = Core_Temp
        self.cold = cold
        self.opt = opt
        self.hot = hot
        self.wear = wear


class TyreWindow():
    Opt_Label = None
    window = None

    def __init__(self, TyreName, RenderTyre, Starting_Label_No):
        self.TyreName = TyreName
        self.window = ac.newApp(TyreName)
        self.Starting_Label_No = Starting_Label_No
        ac.setSize(self.window, 100, 120)
        Opt_Label = ac.addLabel(self.window, "%")
        ac.setPosition(Opt_Label, 30, 70)
        for i in range(3):
            Labels_Dict[self.Starting_Label_No+i] = ac.addLabel(self.window, "")
        ac.addRenderCallback(self.window, RenderTyre)


class Switch():
    button = None

    def __init__(self, posX, posY, sizeX, sizeY, Font_Size, function):
        self.button = ac.addButton(appWindow, "")
        ac.addOnClickedListener(self.button, function)
        self.posX = posX
        self.posY = posY
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.Font_Size = Font_Size
        self.ConfigureButton()

    def ConfigureButton(self):
        ac.setPosition(self.button, self.posX, self.posY)
        ac.setSize(self.button, self.sizeX, self.sizeY)
        ac.setBackgroundOpacity(self.button, 0)
        ac.setFontColor(self.button, 1, 0, 0, 1)
        ac.setFontSize(self.button, self.Font_Size)
        ac.setFontAlignment(self.button, "center")


class Driver():
    def __init__(self, pb, tempTheoritical, TheoriticalBest, NormPos,
                 tempTotalLaps, TotalLaps, CurrentLaptime, temppb,
                 PerformanceMeter, CurrentSector, lastSectorTime,
                 currentSectorIndex, numberOfLaps):
        self.pb = pb
        self.tempTheoritical = tempTheoritical
        self.TheoriticalBest = TheoriticalBest
        self.NormPos = NormPos
        self.tempTotalLaps = tempTotalLaps
        self.TotalLaps = TotalLaps
        self.CurrentLaptime = CurrentLaptime
        self.temppb = temppb
        self.PerformanceMeter = PerformanceMeter
        self.CurrentSector = CurrentSector
        self.lastSectorTime = lastSectorTime
        self.currentSectorIndex = currentSectorIndex
        self.numberOfLaps = numberOfLaps


class Car():
    def __init__(self, RPM, MaxRPM, speed, maxspeed, gForces, Gear,
                 StartingFuel, TC, ABS, DRS, PIT_LIMITER, pitLimiterFLAG,
                 fuel, maxFuel, tyreCompound):
        self.RPM = RPM
        self.MaxRPM = MaxRPM
        self.speed = speed
        self.maxspeed = maxspeed
        self.gForces = gForces
        self.Gear = Gear
        self.StartingFuel = StartingFuel
        self.TC = TC
        self.ABS = ABS
        self.DRS = DRS
        self.PIT_LIMITER = PIT_LIMITER
        self.pitLimiterFLAG = pitLimiterFLAG
        self.fuel = fuel
        self.maxFuel = maxFuel
        self.tyreCompound = tyreCompound


class DashBoard():

    def __init__(self, VIS_RPM_KMH, VIS_TIMES, VIS_FUEL, VIS_POS_LAPS, VIS_SECTOR):
        self.VIS_RPM_KMH = VIS_RPM_KMH
        self.VIS_TIMES = VIS_TIMES
        self.VIS_FUEL = VIS_FUEL
        self.VIS_POS_LAPS = VIS_POS_LAPS
        self.VIS_SECTOR = VIS_SECTOR


FL = Tyres(0, 0, 0, 0, 0)
FR = Tyres(0, 0, 0, 0, 0)
RL = Tyres(0, 0, 0, 0, 0)
RR = Tyres(0, 0, 0, 0, 0)
Driver_0 = Driver(0, {}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
Car_0 = Car(0, 0, 0, 0, (0, 0), 0, 0, 0, 0, 0, 0, False, 0, 0, "")
Dashboard_0 = DashBoard(0, 0, 2, 0, 0)
###########################################################################################     Switches   ##########################################################


def switch_Sector(x, y):
    if Car_0.PIT_LIMITER == 0:
        if Dashboard_0.VIS_SECTOR == 0:
            Dashboard_0.VIS_SECTOR = 1
        else:
            Dashboard_0.VIS_SECTOR = 0


def check_switch_sector():
    if Dashboard_0.VIS_SECTOR == 0:
        try:
            if Driver_0.TotalLaps == 0 and Driver_0.currentSectorIndex > 0:
                ac.setFontColor(Sector.button, 1, 0, 1, 1)
                ac.setText(Sector.button, "{0}".format(int_to_time(Driver_0.lastSectorTime)))
            elif Driver_0.currentSectorIndex == 0:
                if Driver_0.lastSectorTime < Driver_0.tempTheoritical["S" + str(len(list(Driver_0.tempTheoritical.keys())) - 1)][1]:
                    ac.setFontColor(Sector.button, 1, 0, 1, 1)
                else:
                    ac.setFontColor(Sector.button, 1, 1, 0, 1)
            elif Driver_0.lastSectorTime < Driver_0.tempTheoritical[list(Driver_0.tempTheoritical.keys())[Driver_0.currentSectorIndex - 1]][0]:
                ac.setFontColor(Sector.button, 1, 0, 1, 1)
            else:
                ac.setFontColor(Sector.button, 1, 1, 0, 1)
            ac.setText(Sector.button, "{0}".format(int_to_time(Driver_0.lastSectorTime)))
        except:
            if Driver_0.TotalLaps == 1 and Driver_0.currentSectorIndex == 0:
                ac.setFontColor(Sector.button, 1, 0, 1, 1)
                ac.setText(Sector.button, "{0}".format(int_to_time(Driver_0.lastSectorTime)))
            else:
                ac.setText(Sector.button, "No Sector")
    else:
        if Driver_0.TotalLaps == 0:
            ac.setText(Sector.button, "No Laps")
        else:
            if Driver_0.PerformanceMeter > 0:
                ac.setFontColor(Sector.button, 1, 0, 0, 1)
                ac.setText(Sector.button, "+{0}".format(round(Driver_0.PerformanceMeter, 1)))
            else:
                ac.setFontColor(Sector.button, 0, 1, 0, 1)
                ac.setText(Sector.button, "{0}".format(round(Driver_0.PerformanceMeter, 1)))


def switch_fuel(x, y):
    if Car_0.PIT_LIMITER == 0:
        if Dashboard_0.VIS_FUEL == 0:
            Dashboard_0.VIS_FUEL = 1
        elif Dashboard_0.VIS_FUEL == 1:
            Dashboard_0.VIS_FUEL = 2
        else:
            Dashboard_0.VIS_FUEL = 0


def switch_times(x, y):
    if Car_0.PIT_LIMITER == 0:
        if Dashboard_0.VIS_TIMES == 0:
            Dashboard_0.VIS_TIMES = 1
        else:
            Dashboard_0.VIS_TIMES = 0


def check_switch_times():
    if Dashboard_0.VIS_TIMES == 0:
        ac.setText(Times.button, "{0}".format(int_to_time(Driver_0.pb)))
        ac.setFontColor(Times.button, 1, 0, 0, 1)
    else:
        ac.setText(Times.button, "{0}".format(int_to_time(Driver_0.TheoriticalBest)))
        ac.setFontColor(Times.button, 0.5, 0, 1, 1)


def switch_RPM_KMh(x, y):
    if Car_0.PIT_LIMITER == 0:
        if Dashboard_0.VIS_RPM_KMH == 0:
            Dashboard_0.VIS_RPM_KMH = 1
        elif Dashboard_0.VIS_RPM_KMH == 1:
            Dashboard_0.VIS_RPM_KMH = 2
        else:
            Dashboard_0.VIS_RPM_KMH = 0


def check_switch_RPM_KMh():
    if Dashboard_0.VIS_RPM_KMH == 1:
        ac.setText(RPM_KMH.button, "{0}".format(round(Car_0.maxspeed)))
        ac.setFontColor(RPM_KMH.button, 0.5, 0, 1, 1)
    elif Dashboard_0.VIS_RPM_KMH == 2:
        ac.setText(RPM_KMH.button, "{0}".format(round(Car_0.RPM)))
        ac.setFontColor(RPM_KMH.button, 1, 0, 0, 1)
    else:
        ac.setText(RPM_KMH.button, "{0}".format(round(Car_0.speed)))


def switch_Pos_Laps(x, y):
    if Car_0.PIT_LIMITER == 0:
        if Dashboard_0.VIS_POS_LAPS == 0:
            Dashboard_0.VIS_POS_LAPS = 1
        else:
            Dashboard_0.VIS_POS_LAPS = 0


def check_switch_Pos_Laps():
    if Dashboard_0.VIS_POS_LAPS == 0:
        ac.setText(Pos_Laps.button, "L: {0}/{1}".format(Driver_0.TotalLaps + 1, Driver_0.numberOfLaps))
    else:
        ac.setText(Pos_Laps.button, "P: {0}/{1}".format(position, numCars))


def check_Driver_Pos():
    global position
    position = ac.getCarRealTimeLeaderboardPosition(0) + 1


def getUserSettings():
    global RacingMode, UserAssists, AmbientTemp
    CfgFolder = glob("C://Users//*//Documents//Assetto Corsa//cfg//")[0]
    config = configparser.ConfigParser(inline_comment_prefixes=(';'))

    config.read(CfgFolder + 'race.ini')
    tempnationality = config['CAR_0']['NATIONALITY']
    nationality = lambda x: '' if x == 'Planet Earth' else x
    AmbientTemp = float(config['TEMPERATURE']['ambient'])

    config.read(CfgFolder+'controls.ini')
    InputController = config['HEADER']['INPUT_METHOD']

    config.read(CfgFolder+'launcher.ini')
    mode = config['SAVED']['DRIVE']
    racingMode = lambda x: "Special Event" if x == 'specialevents' else 'Time Attack' if x == 'timeattack' else x.capitalize()
    RacingMode = racingMode(mode)
    UserSETTINGS.extend((nationality(tempnationality), InputController, RacingMode))

    config.read(CfgFolder+'assists.ini')
    help = config['ASSISTS']
    UserAssists = ["Off" if help[i] == "0" else help[i] if i in ("stability_control", "damage", "fuel_rate", "tyre_wear") else "On" for i in help]


def acMain(Ptyxiakh):
    global appWindow, nickname, track, car
    appWindow = ac.newApp("")
    ac.setSize(appWindow, 600, 170)
    ac.drawBorder(appWindow, 0)
    Driver_0.pb = 0
    for i in range(0, len(ac.getLastSplits(0))):
        Driver_0.tempTheoritical['S'+str(i)] = []

    check_log_file()
    getUserSettings()
    track = change_track_name(ac.getTrackName(0))
    upgrade, car = change_car_name(ac.getCarName(0))
    UserSETTINGS.append(upgrade)
    addLabels2()
    addLabels()
    nickname = ac.getDriverName(0)
    Car_0.MaxRPM = MaxRPM(ac.getCarName(0))

    background = ac.addLabel(appWindow, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 600, 170)
    ac.setBackgroundTexture(background, app_dir + "/Images/Dashboard.png")
    return "AC-Ranking"


def acUpdate(deltaT):
    Driver_0.NormPos = ac.getCarState(0,acsys.CS.NormalizedSplinePosition)
    Driver_0.tempTotalLaps=ac.getCarState(0,acsys.CS.LapCount)
    Driver_0.CurrentLaptime=ac.getCarState(0,acsys.CS.LapTime)
    Driver_0.temppb=ac.getCarState(0,acsys.CS.BestLap)
    Car_0.speed=ac.getCarState(0,acsys.CS.SpeedKMH)
    Car_0.RPM=ac.getCarState(0,acsys.CS.RPM)
    FL.Core_Temp,FR.Core_Temp,RL.Core_Temp,RR.Core_Temp=ac.getCarState(0,acsys.CS.CurrentTyresCoreTemp)
    Save_Max_Speed(Car_0.speed)
    ReadSharedMemory()
    Car_0.gForces=ac.getCarState(0,acsys.CS.AccG)
    Car_0.Gear=ac.getCarState(0,acsys.CS.Gear)
    checkECU()
    Driver_0.PerformanceMeter=ac.getCarState(0,acsys.CS.PerformanceMeter)
    SetDashboardLabels(Car_0.Gear)

    if Driver_0.TotalLaps<Driver_0.tempTotalLaps:
        Driver_0.TotalLaps=Driver_0.tempTotalLaps
        MeasureFuelLaps(Car_0.fuel)
        search_splits(ac.getLastSplits(0))
        Lastlap=sum(ac.getLastSplits(0))
        for label,tyre in zip(HotColdTyreLabels,(FL,FR,RL,RR)):
            ac.setText(label,"Opt: {}%".format(round((tyre.opt*100)/Lastlap,1)))
            tyre.opt=0
            tyre.cold=0
            tyre.hot=0

    if Driver_0.CurrentSector!=Driver_0.currentSectorIndex:
         Driver_0.CurrentSector=Driver_0.currentSectorIndex

    if Driver_0.temppb>0 and (Driver_0.pb==0 or Driver_0.temppb<Driver_0.pb):
        Driver_0.pb=Driver_0.temppb
        checkTime(Driver_0.temppb)

    if round(FL.Core_Temp,1)==round(FR.Core_Temp,1)==round(RL.Core_Temp,1)==round(RR.Core_Temp,1)==AmbientTemp and (len(str(Car_0.fuel))==4 or track=="Assetto Dorifto track"):
        Reset_Values()
########################################################################################


def SetDashboardLabels(Gear):
    if Gear==0:
        Gear="R"
    elif Gear==1:
        Gear="N"
    else:
        Gear-=1
    ac.setText(Labels_Dict[32],"{0}".format(Gear))
    check_switch_RPM_KMh()
    check_Driver_Pos()
    check_switch_Pos_Laps()
    check_switch_times()
    check_switch_sector()
    if Car_0.PIT_LIMITER>0:
        ac.setText(RPM_KMH.button,"IN PIT")
        for button in (Sector.button,Times.button):
            ac.setText(button,"")
        ac.setText(Pos_Laps.button,"P: {0}/{1}".format(position,numCars))
        Dashboard_0.VIS_POS_LAPS=1
        for label in FuelLabels:
            ac.setVisible(label,0)

        for button in (RPM_KMH.button,Pos_Laps.button,Sector.button):
            if 500<int(str(Driver_0.CurrentLaptime)[-3:])<999:
                ac.setText(button,"")
        Car_0.pitLimiterFLAG=True       
    else:
        if 0<Car_0.RPM<10:
            Car_0.RPM=0
        elif Car_0.RPM<0:
            Car_0.RPM=-Car_0.RPM

    if Car_0.PIT_LIMITER==0 and Car_0.pitLimiterFLAG==True:
        for button in (RPM_KMH.button,Pos_Laps.button,Sector.button,Times.button):
            ac.setVisible(button,1)
        for label in FuelLabels:
            ac.setVisible(label,1)
        Car_0.pitLimiterFLAG=False


def checkECU():
    if Car_0.DRS>0:
        ac.setVisible(ECULabels[0],1)
    else:
        ac.setVisible(ECULabels[0],0)
    if Car_0.ABS>0:
        ac.setVisible(ECULabels[1],1)
    else:
        ac.setVisible(ECULabels[1],0)
    if Car_0.TC>0:
        ac.setVisible(ECULabels[2],1)
    else:
        ac.setVisible(ECULabels[2],0)


def Save_Max_Speed(speed):
    if speed>Car_0.maxspeed:
        Car_0.maxspeed=round(speed,1)


def checkTime(pb):
    global LogFileTrack,LogFileCar,LogFileLap
    splits=ac.getLastSplits(0)
    while len(splits)<3:
        splits.append(0)

    if LogFileTrack==track and LogFileCar==car:
        if LogFileLap==0 or LogFileLap>pb:
            pass
            #Popen([Python,Client,nickname,track,car,str(pb),str(Car_0.maxspeed)]+list(map(str,splits))+UserAssists+UserSETTINGS)
    else:
        LogFileTrack=track
        LogFileCar=car
        LogFileLap=pb   
        #Popen([Python,Client,nickname,track,car,str(pb),str(Car_0.maxspeed)]+list(map(str,splits))+UserAssists+UserSETTINGS)

    tempdata=[track,car,pb]
    with open(log,'w') as tempfile:
        json.dump(tempdata,tempfile)


def check_log_file():
    global LogFileTrack,LogFileCar,LogFileLap
    try:
        with open(log) as fob:
            tempdata=json.load(fob)
            LogFileTrack=tempdata[0]
            LogFileCar=tempdata[1]
            LogFileLap=tempdata[2]          
    except IOError:
        tempdata=['track','car',0]
        with open(log,'w') as tempfile:
            json.dump(tempdata,tempfile)


def onFormRender(deltaT):
    for label,temp in zip(TyreLabels,(FL.Core_Temp,FR.Core_Temp,RL.Core_Temp,RR.Core_Temp)):
        ac.setText(label,"{}C".format(round(temp)))

    ac.glColor4f(1,1,1,1)                                                           # RESET COLORS
    drawDashboard()


def drawGForces():
    ac.glColor3f(1,1,0)
    if Car_0.gForces[2]>0.05:
        ac.glQuadTextured(104,119,20,20,ImageArrowDown)
    elif Car_0.gForces[2]<-0.05:
        ac.glQuadTextured(104,119,20,20,ImageArrowUp)

    if Car_0.gForces[0]>0.05:
        ac.glQuadTextured(132,147,20,20,ImageArrowRight)
    elif Car_0.gForces[0]<-0.05:
        ac.glQuadTextured(130,148,20,20,ImageArrowLeft)
    ac.setText(Gforces[0],"{0}".format(abs(round(Car_0.gForces[2],1))))
    ac.setText(Gforces[1],"{0}".format(abs(round(Car_0.gForces[0],1))))


def drawDashboard():
    if Car_0.RPM<10:
        pass
    elif Car_0.RPM>Car_0.MaxRPM or Car_0.PIT_LIMITER>0:
        for i in range(0,5):
            ac.glQuadTextured(144+(i*20),40,32,32,ImageLedGreen)
        for i in range(5,10):
            ac.glQuadTextured(144+(i*20),41,32,32,ImageLedRed)
        for i in range(10,15):
            ac.glQuadTextured(144+(i*20),41,32,32,ImageLedBlue)
    else:
        if car=="Formula Abarth":
            for i in range(0,round(Car_0.RPM*3/Car_0.MaxRPM)):
                if i==0:
                    for i in range(0,5):
                        ac.glQuadTextured(144+(i*20),40,32,32,ImageLedGreen)
                elif i==1 and Car_0.RPM>4500:
                    for i in range(5,10):
                        ac.glQuadTextured(144+(i*20),41,32,32,ImageLedRed)
                elif i==2 and Car_0.RPM>6300:
                    for i in range(10,15):
                        ac.glQuadTextured(144+(i*20),41,32,32,ImageLedBlue)
        else:
            for i in range(0,round(Car_0.RPM*15/Car_0.MaxRPM)):
                if 0<=i<5:
                    ac.glQuadTextured(144+(i*20),40,32,32,ImageLedGreen)
                elif 5<=i<10:
                    ac.glQuadTextured(144+(i*20),41,32,32,ImageLedRed)
                else:
                    ac.glQuadTextured(144+(i*20),41,32,32,ImageLedBlue)
    if Car_0.PIT_LIMITER>0:
        if 500<int(str(Driver_0.CurrentLaptime)[-3:])<999:
            ac.glQuadTextured(129,67,343,38,ImageLedsYellow)


def search_splits(splits):
    temptp=0
    if Driver_0.tempTheoritical:
        for i in range(0,len(splits)):
            Driver_0.tempTheoritical['S'+str(i)].append(splits[i])
            Driver_0.tempTheoritical['S'+str(i)]=sorted(Driver_0.tempTheoritical['S'+str(i)])
            temptp+=Driver_0.tempTheoritical['S'+str(i)][0]
        if Driver_0.TheoriticalBest==0 and temptp>0:
            Driver_0.TheoriticalBest=temptp
        elif temptp<Driver_0.TheoriticalBest:
            Driver_0.TheoriticalBest=temptp


def RenderTyreFL(deltaT):
    drawTyreColors(FL.Core_Temp,WindowFL.window)
    measureHotCold(FL.Core_Temp,FL)


def RenderTyreFR(deltaT):
    drawTyreColors(FR.Core_Temp,WindowFR.window)
    measureHotCold(FR.Core_Temp,FR)


def RenderTyreRL(deltaT):
    drawTyreColors(RL.Core_Temp,WindowRL.window)
    measureHotCold(RL.Core_Temp,RL)


def RenderTyreRR(deltaT):
    drawTyreColors(RR.Core_Temp,WindowRR.window)
    measureHotCold(RR.Core_Temp,RR)


def drawTyreColors(temp,window):
    global HotColdTyreLabels
    if temp<TyreComps[Car_0.tyreCompound][0]:
        ac.setBackgroundColor(window,0,0,1)
    elif temp>TyreComps[Car_0.tyreCompound][1]:
        ac.setBackgroundColor(window,1,0,0)
    else:
        ac.setBackgroundColor(window,0,1,0)

    ac.setBackgroundOpacity(window,0.5)
    ac.drawBorder(window,0)


def measureHotCold(temp,Tyre):

    if temp<TyreComps[Car_0.tyreCompound][0]:
        Tyre.cold=Driver_0.CurrentLaptime-(Tyre.opt+Tyre.hot)
    elif temp>TyreComps[Car_0.tyreCompound][1]:
        Tyre.hot=Driver_0.CurrentLaptime-(Tyre.opt+Tyre.cold)
    else:
        Tyre.opt=Driver_0.CurrentLaptime-(Tyre.hot+Tyre.cold)


def addLabels2():
    global WindowFL,WindowFR,WindowRL,WindowRR,TyreLabels,HotColdTyreLabels
    WindowFL=TyreWindow("F_R",RenderTyreFL,9)
    WindowFR=TyreWindow("F_L",RenderTyreFR,14)
    WindowRL=TyreWindow("R_R",RenderTyreRL,19)
    WindowRR=TyreWindow("R_L",RenderTyreRR,24)
    HotColdTyreLabels=[WindowFL.Opt_Label,WindowFR.Opt_Label,WindowRL.Opt_Label,WindowRR.Opt_Label]
    TyreLabels=[Labels_Dict[9],Labels_Dict[14],Labels_Dict[19],Labels_Dict[24]]
    for label in TyreLabels:
        ac.setFontSize(label,25)
        ac.setPosition(label,35,30)


def addLabels():
    global FuelLabels,Gforces,ECULabels,ElectronicLabels
    global ImageArrowUp,ImageArrowDown,ImageArrowRight,ImageArrowLeft
    global ImageLedRed,ImageLedGreen,ImageLedBlue,ImageLedsYellow
    global RPM_KMH,Times,Pos_Laps,Sector
    WindowInfo=ac.newApp("Info")
    ac.setSize(WindowInfo,160,205)
    ac.addRenderCallback(WindowInfo,RenderInfo)

    for i in range(32,44):
        if i==33:
            Labels_Dict[i]=ac.addProgressBar(appWindow,"")
            ac.setSize(Labels_Dict[i],65,17)
            ac.setFontColor(Labels_Dict[i],1,0.56,0,1)
            ac.setBackgroundColor(Labels_Dict[i],1,1,0)
            ac.drawBackground(Labels_Dict[i],1)
            ac.drawBorder(Labels_Dict[i],0)
        elif i in (35,36,37,38,39,40):
            Labels_Dict[i]=ac.addLabel(WindowInfo,"")
        elif i in (41,42,43):
            Labels_Dict[i]=ac.addLabel(WindowInfo,"")
            ac.setSize(Labels_Dict[i],30,30)
            ac.setBackgroundTexture(Labels_Dict[i],app_dir+"/Images/on.png")
            ac.setVisible(Labels_Dict[i],0)
        else:                                                   #Benzinh,Taxuthtes
            Labels_Dict[i]=ac.addLabel(appWindow,"")

    ac.setFontColor(Labels_Dict[32],1,0,0,1)
    ac.setFontSize(Labels_Dict[32],40)
    ac.setFontColor(Labels_Dict[34],0,0,0,1)

    FuelLabels=[Labels_Dict[33],Labels_Dict[34]]
    ElectronicLabels=[Labels_Dict[35],Labels_Dict[36],Labels_Dict[37],Labels_Dict[38]]
    Gforces=[Labels_Dict[39],Labels_Dict[40]]
    ECULabels=[Labels_Dict[41],Labels_Dict[42],Labels_Dict[43]]
#------------------------------------------------------
    appWindowLabels=[Labels_Dict[32]]+FuelLabels+ElectronicLabels+Gforces+ECULabels
    Positions=[(290,58),    #Dashboard Labels(Gear,RPM/Speed,Pos/Laps,lastSectorTime/PerformanceMeter,LastLap)
                (181,105),(183,103),  #progressbar/Fuel,Pre,Est
                (50,35),(10,55),(35,120),(35,150), #Tyres/Optimum temps/ABS/TC
                (133,119),(103,145), #Gforces
                (400,7),(3,114),(3,144) #ECU Images(on)
                ]

    for label,pos in zip(appWindowLabels,Positions):
        ac.setPosition(label,pos[0],pos[1])

    for i in ElectronicLabels:
        ac.setFontSize(i,12)

    ImageArrowUp=ac.newTexture(app_dir+"/Images/arrowUp.png")
    ImageArrowDown=ac.newTexture(app_dir+"/Images/arrowDown.png")
    ImageArrowRight=ac.newTexture(app_dir+"/Images/arrowRight.png")
    ImageArrowLeft=ac.newTexture(app_dir+"/Images/arrowLeft.png")
    ImageLedRed=ac.newTexture(app_dir+"/Images/LedRed.png")
    ImageLedGreen=ac.newTexture(app_dir+"/Images/LedGreen.png")
    ImageLedBlue=ac.newTexture(app_dir+"/Images/LedBlue.png")
    ImageLedsYellow=ac.newTexture(app_dir+"/Images/LedsYellow.png")
    ac.addRenderCallback(appWindow,onFormRender)

    RPM_KMH=Switch(365,70,80,30,25,switch_RPM_KMh)
    Times=Switch(270,104,80,20,15,switch_times)
    Fuel=Switch(181,105,65,18,15,switch_fuel)
    Pos_Laps=Switch(163,70,80,30,25,switch_Pos_Laps)
    Sector=Switch(365,104,80,20,15,switch_Sector)

    background=ac.addLabel(WindowInfo,"")                   # Prepei na mpei teleytaio gia na fortwnei meta to prasino eikonidio gia na kratietai to diafano...
    ac.setPosition(background,0,0)
    ac.setSize(background,161,205)
    ac.setBackgroundTexture(background,app_dir+"/Images/Info"+UserSETTINGS[-1]+".png")
###########################################################################################     Info   ##########################################################


def RenderInfo(deltaT):
    drawGForces()
###########################################################################################     RESET   ##########################################################


def Reset_Values():
    Car_0.maxspeed=0
    Driver_0.TotalLaps=0
    Car_0.StartingFuel=0

###########################################################################################     SHARED MEMORY   ##########################################################


def ReadSharedMemory():
    Car_0.TC=info.physics.tc
    Car_0.ABS=info.physics.abs
    Car_0.DRS=info.physics.drs
    Car_0.PIT_LIMITER=info.physics.pitLimiterOn
    check_TC_ABS(round(Car_0.TC,2),round(Car_0.ABS,2),Car_0.DRS)

    Car_0.fuel=info.physics.fuel

    if Car_0.StartingFuel==0:
        Car_0.StartingFuel=Car_0.fuel
    if STATICSharedMemoryFLAG==True:
        ReadSTATICSharedMemory()

    FuelIndicator(Car_0.fuel,Car_0.maxFuel)
    FL.wear,FR.wear,RL.wear,RR.wear=list(info.physics.tyreWear)

    Car_0.tyreCompound=info.graphics.tyreCompound
    Driver_0.lastSectorTime=info.graphics.lastSectorTime
    Driver_0.currentSectorIndex=info.graphics.currentSectorIndex

    if Car_0.tyreCompound:
        SetCompound(Car_0.tyreCompound)

    Driver_0.numberOfLaps=info.graphics.numberOfLaps


def ReadSTATICSharedMemory():
    global STATICSharedMemoryFLAG,numCars

    Car_0.maxFuel=info.static.maxFuel
    ac.setRange(FuelLabels[0],0,Car_0.maxFuel)
    numCars=info.static.numCars

    STATICSharedMemoryFLAG=False


def check_TC_ABS(tc,ABS,drs):
    Values={
        '500 EsseEsse':(1,1),
        '1M':(1,1),
        'M3 E30 Sport Evolution':(0,1),
        'M3 E30 Group A':(0,1),
        'M3 E92':(1,1),
        'M3 GT2':(1,0),
        'Z4 E89 35is':(1,1),
        'Z4 GT3':((0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.20,0.21,0.22),1),
        '312T':(0,0),
        '458 Italia':((0.10,0.14,0.18,0.24),1),
        '599xx EVO':((0.10,0.11,0.12,0.14,0.16,0.18,0.20,0.22,0.24),1),
        'F40':(0,0),
        'X-Bow R':(0,1),
        '2-Eleven':((0.13,0.20,0.27),1),
        'Type 49':(0,0),
        'Elise SC':((0.11,0.17),1),
        'Evora S':((0.13,0.20,0.27),1),
        'Evora GTC':((0.08,0.09,0.10,0.11,0.12,0.14,0.16,0.18,0.20,0.22,0.24),1),
        'Evora GTE':((0.13,0.20,0.27),1),
        'Evora GX':(0,0),
        'Exige 240':((0.13,0.2,0.27),1),
        'Exige S Roadster':((0.13,0.20,0.27),1),
        'Exige Scura':((0.13,0.20,0.27),1),
        'Exos 125':((0.05,0.1,0.15,0.2,0.25),0),
        'MP4-12C':((0.16,0.30),1),
        'MP4-12C GT3':((0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.08,0.09,0.10),1),
        'P45 Competizione':(1,1),
        'Huayra':((0.12,0.17,0.22,0.4),1),
        'Zonda R':(
            (0.08,0.09,0.10,0.11,0.12,0.14,0.16,0.18,0.20,0.22,0.24),
            (0.08,0.09,0.10,0.11,0.12,0.14,0.16,0.18,0.20,0.22,0.24)
            ),
        'Formula Abarth':(0,0)
        }
    #Check if Car is a Mod to create its values from reading its file with ABS/TC values inside game's folder
    #config = configparser.ConfigParser(inline_comment_prefixes=(';'))


    #ABS#
    if car in Values:
        if type(Values[car][1])==int:
            pass
        else:
            if ABS>0:
                ac.setText(ElectronicLabels[2],"{}/{}".format(Values[car][1].index(ABS)+1,len(Values[car][1])))
            else:
                ac.setText(ElectronicLabels[2],"")
            #TC#
        if type(Values[car][0])==int:
            pass
        else:
            if tc>0:
                ac.setText(ElectronicLabels[3],"{}/{}".format(Values[car][0].index(tc)+1,len(Values[car][0])))
            else:
                ac.setText(ElectronicLabels[3],"")
    else:
        TC_File=game_dir+"\\content\\cars\\"+ac.getCarName(0)+"\\data\\traction_control.lut"
        if os.path.isfile(TC_File)==True:
            with open(TC_File) as f:
                TC_Values=f.read()
            TC_Values_list=TC_Values.split()
            Car_TC_Values=tuple([float(x.split("|")[1]) for x in TC_Values_list])
            Values[car]=(Car_TC_Values,1)
        else:
            Values[car]=(0,1)


def SetCompound(compound):
    global TyreComps
    TyreComps={
                    'Street':(75,85),
                    'Semislicks':(75,100),
                    #GT2
                    'Slick SuperSoft':(90,105),'Slick Soft':(90,105),'Slick Medium':(85,105),'Slick Hard':(80,100),'Slick SuperHard':(80,100),
                    #GT3
                    'Slicks Soft':(80,110),'Slicks Medium':(75,105),'Slicks Hard':(70,100),
                    'F1 1967':(50,90),
                    'Slicks Soft Gr.A':(0,0),'Slicks Medium gr.A':(0,0),'Slicks Hard gr.A':(0,0),
                    'Slicks Soft DTM90s':(0,0),'Slicks Medium DTM90s':(0,0),'Slicks Hard DTM90s':(0,0),
                    'Street90S':(0,0),
                    'Street 90s':(0,0),
                    'Trofeo Slicks':(0,0),
                    'Soft 70F1':(50,90),
                    'Hard 70F1':(50,90),
                    'Slick Exos':(90,120),
                    'TopGear Record':(0,0)
                }
    ExosTyres={
                    'Slick SuperSoft':(85,110),'Slick Soft':(105,125),'Slick Medium':(90,115),'Slick Hard':(110,135)
                }
    if ac.getCarName(0)=="lotus_exos_125_s1":
        TyreComps=ExosTyres

    if compound in TyreComps:
        ac.setText(ElectronicLabels[0],"{}".format(compound))
        ac.setText(ElectronicLabels[1],"Optimum Temps: {}-{}C".format(TyreComps[compound][0],TyreComps[compound][1]))
    else:
        TyreComps={compound:(0,0)}
        ac.setText(ElectronicLabels[0],"Unknown tyres!")


def MeasureFuelLaps(fuel):
    global LapFuel,EstimatedLaps
    LapFuel=Car_0.StartingFuel-fuel
    EstimatedLaps=round(fuel//LapFuel)
    Car_0.StartingFuel=fuel


def FuelIndicator(fuel,maxFuel):
    ac.setValue(FuelLabels[0],round(fuel))

    if Dashboard_0.VIS_FUEL==0:
        if Driver_0.TotalLaps>0:
            ac.setText(FuelLabels[1],"Pre: {0:.1f}L".format(LapFuel))
        else:
            ac.setText(FuelLabels[1],"Pre: ")
    elif Dashboard_0.VIS_FUEL==1:
        if Driver_0.TotalLaps>0:
            ac.setText(FuelLabels[1],"Laps: {0}".format(EstimatedLaps))
        else:
            ac.setText(FuelLabels[1],"Laps: ")
    else:
        ac.setText(FuelLabels[1],"{0}/{1}L".format(round(fuel),round(maxFuel)))
