import os

import ac

from ptyxiakh import CAR_0 as CAR, DRIVER_0 as DRIVER
from tyres import get_compound_temps


ELECTRONIC_LABELS = {
    35: {'label_no': None, 'pos': (50, 35)},
    36: {'label_no': None, 'pos': (10, 55)},
    37: {'label_no': None, 'pos': (35, 120)},
    38: {'label_no': None, 'pos': (35, 150)}
}
G_FORCES_LABELS = {
    39: {'label_no': None, 'pos': (133, 119)},
    40: {'label_no': None, 'pos': (103, 145)}
}
ECU_LABELS = {
    41: {'label_no': None, 'pos': (400, 7)},
    42: {'label_no': None, 'pos': (3, 114)},
    43: {'label_no': None, 'pos': (3, 144)}
}
IMAGE_ARROW_DOWN = None
IMAGE_ARROW_UP = None
IMAGE_ARROW_LEFT = None
IMAGE_ARROW_RIGHT = None


# FIXME call this function from ptyxiakh(dont forget to pass the args!)
def add_app(app_dir):
    """Add the info window/app."""
    global IMAGE_ARROW_DOWN, IMAGE_ARROW_UP, IMAGE_ARROW_LEFT, IMAGE_ARROW_RIGHT
    window_info = ac.newApp("Info")
    ac.setSize(window_info, 160, 205)
    ac.addRenderCallback(window_info, render_info)

    for label in ELECTRONIC_LABELS:
        label['label_no'] = ac.addLabel(window_info, '')
        ac.setFontSize(label['label_no'], 12)

    for label in G_FORCES_LABELS:
        label['label_no'] = ac.addLabel(window_info, "")

    for label in ECU_LABELS:
        label['label_no'] = ac.addLabel(window_info, "")
        ac.setSize(label['label_no'], 30, 30)
        ac.setBackgroundTexture(label['label_no'], app_dir + "/Images/on.png")
        ac.setVisible(label['label_no'], 0)

    for label_group in (ELECTRONIC_LABELS, G_FORCES_LABELS, ECU_LABELS):
        for label in label_group:
            ac.setPosition(label['label_no'], label['pos'][0], label['pos'][1])

    IMAGE_ARROW_DOWN = ac.newTexture(app_dir + "/Images/arrowDown.png")
    IMAGE_ARROW_UP = ac.newTexture(app_dir + "/Images/arrowUp.png")
    IMAGE_ARROW_RIGHT = ac.newTexture(app_dir + "/Images/arrowRight.png")
    IMAGE_ARROW_LEFT = ac.newTexture(app_dir + "/Images/arrowLeft.png")

    # Prepei na mpei teleytaio gia na fortwnei meta to prasino eikonidio gia na
    # kratietai to diafano...
    background = ac.addLabel(window_info, "")
    ac.setPosition(background, 0, 0)
    ac.setSize(background, 161, 205)
    car_upgrade_img_path = os.path.join(
        app_dir, "/Images/Info{}.png".format(DRIVER.settings['car_upgrade']))
    ac.setBackgroundTexture(background, car_upgrade_img_path)


def render_info(deltaT):
    ac.glColor3f(1, 1, 0)
    if CAR.g_forces[2] > 0.05:
        ac.glQuadTextured(104, 119, 20, 20, IMAGE_ARROW_DOWN)
    elif CAR.g_forces[2] < -0.05:
        ac.glQuadTextured(104, 119, 20, 20, IMAGE_ARROW_UP)

    if CAR.g_forces[0] > 0.05:
        ac.glQuadTextured(132, 147, 20, 20, IMAGE_ARROW_RIGHT)
    elif CAR.g_forces[0] < -0.05:
        ac.glQuadTextured(130, 148, 20, 20, IMAGE_ARROW_LEFT)
    ac.setText(G_FORCES_LABELS[39]['label_no'],
               "{0}".format(abs(round(CAR.g_forces[2], 1))))
    ac.setText(G_FORCES_LABELS[40]['label_no'],
               "{0}".format(abs(round(CAR.g_forces[0], 1))))


def switch_ecu_labels():
    ac.setVisible(ECU_LABELS[41]['label_no'], 1 if CAR.drs else 0)
    ac.setVisible(ECU_LABELS[42]['label_no'], 1 if CAR.abs else 0)
    ac.setVisible(ECU_LABELS[43]['label_no'], 1 if CAR.tc else 0)


def update_ecu_labels():
    """Update the values of the ecu labels."""
    tc_text = ''
    if len(CAR.tc_levels) > 2:
        tc_text = '{}/{}'.format(CAR.tc_level, len(CAR.tc_levels))
    ac.setText(ELECTRONIC_LABELS[38]['label_no'], tc_text)

    abs_text = ''
    if len(CAR.abs_levels) > 2:
        abs_text = '{}/{}'.format(CAR.abs_level, len(CAR.abs_levels))
    ac.setText(ELECTRONIC_LABELS[37]['label_no'], abs_text)

    if CAR.tyre_compound:
        # TODO: this should be a property for Car() and should be set when
        # .tyre_compound is set(once)
        ac.setText(ELECTRONIC_LABELS[35]['label_no'], CAR.tyre_compound)
        min_temp, max_temp = get_compound_temps(CAR.name, CAR.tyre_compound)
        ac.setText(ELECTRONIC_LABELS[36]['label_no'],
                   "Optimum Temps: {}-{}C".format(min_temp, max_temp))

