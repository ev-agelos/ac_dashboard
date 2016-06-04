from subprocess import *
import os
import json

app_dir=os.path.split(os.path.abspath(__file__))[0]
Client=os.path.join(app_dir, "Python33", "Client.py")
Python=os.path.join(app_dir, "Python33", "python.exe")



username="djbokoboko"
track="Imola"
car="Z4 E89 35is"
besttime="60001"
maxspeed="195.4"
split1="30151"
split2="20000"
split3="0"
idealLine="Off"
autoBlip="Off"
stabilityControl="Off"
autoBrake="Off"
autoShifter="Off"
aBs="Off"
tractionControl="Off"
autoClutch="Off"
visualDamage="Off"
damage="Off"
fuelRate="1"
tyreWear="1"
nationality="Greece"
inputController="Wheel"
racingMode="Hotlap"
carUpgrades="s1"
Popen([Python,Client,
       username,
       track,
       car,
       besttime,
       maxspeed,
       split1,
       split2,
       split3,
       idealLine,
       autoBlip,
       stabilityControl,
       autoBrake,
       autoShifter,
       aBs,
       tractionControl,
       autoClutch,
       visualDamage,
       damage,
       fuelRate,
       tyreWear,
       nationality,
       inputController,
       racingMode,
       carUpgrades])

