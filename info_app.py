import os

import ac

from ui_elements import UILabel
from textures import Texture
from telemetry_provider import TelemetryProvider


APP_DIR = os.path.dirname(os.path.realpath(__file__))
CAR_INFO_APP_TELEMETRY = TelemetryProvider()


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


def info_app(car_upgrade):
    """Add the info window/app."""
    window_info = ac.newApp("Info")
    ac.setSize(window_info, 160, 205)
    ac.addRenderCallback(window_info, render_app)

    compound_label = CompoundLabel(CAR_INFO_APP_TELEMETRY)
    optimum_temps_label = OptimumTempsLabel(CAR_INFO_APP_TELEMETRY)
    abs_label = ABSLabel(CAR_INFO_APP_TELEMETRY)
    tc_label = TractionControlLabel(CAR_INFO_APP_TELEMETRY)

    lateral_force_label = LateralForceLabel(CAR_INFO_APP_TELEMETRY)
    transverse_force_label = TransverseForceLabel(CAR_INFO_APP_TELEMETRY)

    drs_image_label = DRSImageLabel(CAR_INFO_APP_TELEMETRY)
    abs_image_label = ABSImageLabel(CAR_INFO_APP_TELEMETRY)
    tc_image_label = TCImageLabel(CAR_INFO_APP_TELEMETRY)

    background_label = BackgroundLabel()

    for label in (compound_label, optimum_temps_label, abs_label, tc_label,
                  lateral_force_label, transverse_force_label, drs_image_label,
                  abs_image_label, tc_image_label, background_label):
        label.window = window_info

    # Prepei na mpei teleytaio gia na fortwnei meta to prasino eikonidio gia na
    # kratietai to diafano...
    car_upgrade_img_path = os.path.join(
        APP_DIR, "Images/Info{}.png".format(car_upgrade or 'STD'))
    background_label.bg_texture = car_upgrade_img_path

    image_arrow_left = LeftLateralForceImage(
        CAR_INFO_APP_TELEMETRY, pos_x=131, pos_y=147, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowLeft.png')
    image_arrow_right = RightLateralForceImage(
        CAR_INFO_APP_TELEMETRY, pos_x=132, pos_y=147, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowRight.png')
    image_arrow_up = PositiveTransverseForceImage(
        CAR_INFO_APP_TELEMETRY, pos_x=104, pos_y=119, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowUp.png')
    image_arrow_down = NegativeTransverseForceImage(
        CAR_INFO_APP_TELEMETRY, pos_x=104, pos_y=120, width=20, height=20,
        color=(1, 1, 0, 1), filename='arrowDown.png')


def render_app(delta_t):
    CAR_INFO_APP_TELEMETRY.update()
