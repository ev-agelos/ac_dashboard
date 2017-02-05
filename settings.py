"""Settings that are set inside the game."""

import os
import configparser
from glob import glob


def _read_config_settings(filename):
    """Return ini settings from file in user's documents."""
    config_folder = glob("C://Users//*//Documents//Assetto Corsa//cfg//")[0]
    config = configparser.ConfigParser(inline_comment_prefixes=(';',))
    config.read(os.path.join(config_folder, filename))
    return config


def get_track_temp():
    """Return track ambient temp defined inside the game."""
    config = _read_config_settings('race.ini')
    return float(config['TEMPERATURE']['ambient'])


def get_user_nationality():
    """Return user's nationality defined inside the game."""
    config = _read_config_settings('race.ini')
    return config['CAR']['NATIONALITY']


def get_controller():
    """Return user control input defined inside the game."""
    config = _read_config_settings('controls.ini')
    return config['HEADER']['INPUT_METHOD']


def get_racing_mode():
    """Return racing mode defined inside the game."""
    config = _read_config_settings('launcher.ini')
    mode = config['SAVED']['DRIVE']
    modes = {'specialevents': 'Special Event', 'timeattack': 'Time Attack'}
    racing_mode = modes.get(mode) or mode.capitalize()
    return racing_mode


def get_user_assists():
    """Return the assists user set inside the game."""
    config = _read_config_settings('assists.ini')
    on_off_assists = ("stability_control", "damage", "fuel_rate", "tyre_wear")
    assists = {}
    for assist, value in config.items('ASSISTS'):
        result = value
        if assist in on_off_assists:
            result = 'Off' if value == '0' else 'On'
        assists.update(assist=result)

    return assists
