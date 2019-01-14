import os

import ac

from ui_elements import UILabel
from textures import Texture
from telemetry_provider import TelemetryProvider


APP_DIR = os.path.dirname(os.path.realpath(__file__))


class CompoundLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(70, 35), bg_opacity=0)
        self.dashboard = dashboard
        self.dashboard.subscribe('compound', self)

    def run(self, telemetry, value):
        self.text = value or ''


class OptimumTempsLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(5, 57), size=(100, 20), bg_opacity=0,
                         text_align='left')
        self.dashboard = dashboard
        self.dashboard.subscribe('optimum_temps', self)

    def run(self, telemetry, value):
        value = "{}-{}C".format(*value) if value != (0, 0) else 'unknown!'
        self.text = "Optimum Temps: {}".format(value)


class ABSLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(35, 120), bg_opacity=0)
        self.dashboard = dashboard
        self.dashboard.subscribe('abs', self)

    def run(self, telemetry, value):
        if len(value['levels']) > 2:
            self.text = '{}/{}'.format(value['level'], len(value['levels']))
        else:
            self.text = ''


class TractionControlLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(35, 150), bg_opacity=0)
        self.dashboard = dashboard
        self.dashboard.subscribe('traction_control', self)

    def run(self, telemetry, value):
        if len(value['levels']) > 2:
            self.text = '{}/{}'.format(value['level'], len(value['levels']))
        else:
            self.text = ''


class LateralForceLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(103, 145), bg_opacity=0)
        self.dashboard = dashboard
        self.dashboard.subscribe('lateral_force', self)

    def run(self, telemetry, value):
        self.text = "{}".format(abs(round(value, 1)))


class TransverseForceLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(133, 119), bg_opacity=0)
        self.dashboard = dashboard
        self.dashboard.subscribe('transverse_force', self)

    def run(self, telemetry, value):
        self.text = "{}".format(abs(round(value, 1)))


class DRSImageLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(400, 7), size=(30, 30), visible=0, bg_opacity=0,
                         bg_texture=APP_DIR+"/Images/on.png")
        self.dashboard = dashboard
        self.dashboard.subscribe('drs', self)

    def run(self, telemetry, value):
        self.visible = int(bool(value))


class ABSImageLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(3, 114), size=(30, 30), visible=0, bg_opacity=0,
                         bg_texture=APP_DIR+"/Images/on.png")
        self.dashboard = dashboard
        self.dashboard.subscribe('abs', self)

    def run(self, telemetry, value):
        self.visible = int(bool(value['value']))


class TCImageLabel(UILabel):

    def __init__(self, dashboard):
        super().__init__(pos=(3, 144), size=(30, 30), visible=0, bg_opacity=0,
                         bg_texture=APP_DIR+"/Images/on.png")
        self.dashboard = dashboard
        self.dashboard.subscribe('traction_control', self)

    def run(self, telemetry, value):
        self.visible = int(bool(value['value']))


class BackgroundLabel(UILabel):

    def __init__(self):
        super().__init__(pos=(0, 0), size=(161, 205), bg_opacity=0)


class RightLateralForceImage(Texture):

    def __init__(self, dashboard, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dashboard = dashboard
        self.dashboard.subscribe('lateral_force', self)

    def run(self, telemetry, value):
        if value > 0.05:
            self.draw()


class LeftLateralForceImage(Texture):

    def __init__(self, dashboard, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dashboard = dashboard
        self.dashboard.subscribe('lateral_force', self)

    def run(self, telemetry, value):
        if value < -0.05:
            self.draw()


class PositiveTransverseForceImage(Texture):

    def __init__(self, dashboard, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dashboard = dashboard
        self.dashboard.subscribe('transverse_force', self)

    def run(self, telemetry, value):
        if value < -0.05:
            self.draw()


class NegativeTransverseForceImage(Texture):

    def __init__(self, dashboard, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dashboard = dashboard
        self.dashboard.subscribe('transverse_force', self)

    def run(self, telemetry, value):
        if value > 0.05:
            self.draw()


def info_app():
    """Add the info window/app."""
    global info_telemetry
    window_info = ac.newApp("Info")
    ac.setSize(window_info, 160, 205)
    ac.addRenderCallback(window_info, render_app)

    info_telemetry = TelemetryProvider()
    compound_label = CompoundLabel(info_telemetry)
    optimum_temps_label = OptimumTempsLabel(info_telemetry)
    abs_label = ABSLabel(info_telemetry)
    tc_label = TractionControlLabel(info_telemetry)

    lateral_force_label = LateralForceLabel(info_telemetry)
    transverse_force_label = TransverseForceLabel(info_telemetry)

    drs_image_label = DRSImageLabel(info_telemetry)
    abs_image_label = ABSImageLabel(info_telemetry)
    tc_image_label = TCImageLabel(info_telemetry)

    background_label = BackgroundLabel()

    for label in (compound_label, optimum_temps_label, abs_label, tc_label,
                  lateral_force_label, transverse_force_label, drs_image_label,
                  abs_image_label, tc_image_label, background_label):
        label.window = window_info

    # Prepei na mpei teleytaio gia na fortwnei meta to prasino eikonidio gia na
    # kratietai to diafano...
    car_name = ac.getCarName(0)
    car_upgrade = ''
    if car_name.endswith(('_s1', '_s2', '_s3', '_drift', '_dtm')):
        car_upgrade = car_name.split('_')[-1]
    car_upgrade_img_path = os.path.join(
        APP_DIR, "Images/Info{}.png".format(car_upgrade or 'STD'))
    background_label.bg_texture = car_upgrade_img_path

    image_arrow_left = LeftLateralForceImage(
        info_telemetry, pos_x=131, pos_y=147, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowLeft.png')
    image_arrow_right = RightLateralForceImage(
        info_telemetry, pos_x=132, pos_y=147, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowRight.png')
    image_arrow_up = PositiveTransverseForceImage(
        info_telemetry, pos_x=104, pos_y=119, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowUp.png')
    image_arrow_down = NegativeTransverseForceImage(
        info_telemetry, pos_x=104, pos_y=120, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowDown.png')


def render_app(delta_t):
    info_telemetry.update()
