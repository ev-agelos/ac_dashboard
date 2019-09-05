# ac_dashboard

App showing car's telemetry and driver's lap times for the game Assetto Corsa

### Installation
Download latest release, **rename** the folder to **ac_dashboard** and place it in Assetto corsa's app folder, example:

>C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\apps\python\ac_dashboard

To enable the app, just click on the right side in the task bar (inside the game)  where all apps exist.

### Information
The app consists of 6 windows:
- main dashboard
- car information
- information for all 4 tyres

#### Dashboard window

- Leds representing RPMs
- Position / Laps (click to toggle)
- Gear indication
- Speed / Max Speed / Digital RPM's (click to toggle)
- Fuel / Last lap fuel consumption / Laps left estimation depending on fuel consumption (click to toggle)
- Best lap time / Theoretical best lap time (click to toggle)
- Sector times / Performance meter (click to toggle)

#### Car information window

- Tyre compound currently loaded to the car
- Optimum tyre temperatures for the loaded compound
- ABS/Traction Control usage indication
- G-force indication

#### Tyre windows

- Temperature of the tyre(core temperature)
- Percentage indication of how long tyres were driven in their optimum temperature
- Color feedback of tyre's temperature:
  - blue(below optimum tyre temperature)
  - green(optimum tyre temperature)
  - red(above optimum tyre temperature)

![alt text](https://github.com/ev-agelos/ac_dashboard/blob/master/Images/ingame_screenshot.jpg "Application inside the game")

*When entering pits dashboard information is hidden and the indication "IN PITS" starts blinking. Only position in the track and fuel information are being shown. Information gets revealed when exiting the pits.*
