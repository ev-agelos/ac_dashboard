# ac_dashboard

App showing car's/driver's information for the game Assetto Corsa

### Installation
Download via github's download button, **rename** the folder to **ac_dashboard** and place it in Assetto corsa's app folder, example:

>C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\apps\python\ac_dashboard

To enable/open the app, just click on the right hand side inside the game in the task bar where all apps exist.

### Information
The app consists of 6 windows:
- main window with the dashboard
- window showing car information
- 4 windows showing information for each tyre

#### Dashboard window

- Leds representing RPM's
- Position / Laps (click to change)
- Gear indication
- Speed / Max Speed / Digital RPM's (click to change)
- Fuel / Last lap fuel burned / Laps left estimation depending on fuel burned (click to change)
- Best lap time / Theoretical best lap time (click to change)
- Sector times / Performance meter (click to change)

#### Car information window

- Tyre compound currently loaded to the car
- Optimum tyre temperatures for the loaded compound
- ABS/Traction Control usage indication
- G forces indication

#### Tyre windows

- Temperature of the tyre(core temperature)
- Percentage indication of how much tyres were driven in their optimum temperature
- Color feedback of tyre's temperature:
  - blue(below optimum tyre temperature)
  - green(optimum tyre temperature)
  - red(over optimum tyre temperature)
