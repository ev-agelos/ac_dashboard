import os

import ac

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
def add_app(app_dir, render_function, car_upgrade):
    """Add the info window/app."""
    global IMAGE_ARROW_DOWN, IMAGE_ARROW_UP, IMAGE_ARROW_LEFT, IMAGE_ARROW_RIGHT
    window_info = ac.newApp("Info")
    ac.setSize(window_info, 160, 205)
    ac.addRenderCallback(window_info, render_function)

    for label, data in ELECTRONIC_LABELS.items():
        data['label_no'] = ac.addLabel(window_info, '')
        ac.setFontSize(data['label_no'], 12)

    for label, data in G_FORCES_LABELS.items():
        data['label_no'] = ac.addLabel(window_info, "")

    for label, data in ECU_LABELS.items():
        data['label_no'] = ac.addLabel(window_info, "")
        ac.setSize(data['label_no'], 30, 30)
        ac.setBackgroundTexture(data['label_no'], app_dir + "/Images/on.png")
        ac.setVisible(data['label_no'], 0)

    for dict_ in (ELECTRONIC_LABELS, G_FORCES_LABELS, ECU_LABELS):
        for _, data in dict_.items():
            ac.setPosition(data['label_no'], data['pos'][0], data['pos'][1])

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
        app_dir, "/Images/Info{}.png".format(car_upgrade))
    ac.setBackgroundTexture(background, car_upgrade_img_path)


def draw_lateral_g_force(force, right=True):
    ac.glColor3f(1, 1, 0)
    if right:
        ac.glQuadTextured(132, 147, 20, 20, IMAGE_ARROW_RIGHT)
    else:
        ac.glQuadTextured(130, 148, 20, 20, IMAGE_ARROW_LEFT)
    ac.setText(G_FORCES_LABELS[39]['label_no'],
               "{0}".format(abs(round(force, 1))))


def draw_transverse_g_force(force, down=True):
    ac.glColor3f(1, 1, 0)
    if down:
        ac.glQuadTextured(104, 119, 20, 20, IMAGE_ARROW_DOWN)
    else:
        ac.glQuadTextured(104, 119, 20, 20, IMAGE_ARROW_UP)
    ac.setText(G_FORCES_LABELS[40]['label_no'],
               "{0}".format(abs(round(force, 1))))


def switch_ecu_labels(drs, abs_, tc):
    ac.setVisible(ECU_LABELS[41]['label_no'], 1 if drs else 0)
    ac.setVisible(ECU_LABELS[42]['label_no'], 1 if abs_ else 0)
    ac.setVisible(ECU_LABELS[43]['label_no'], 1 if tc else 0)


def update_ecu_labels(car, compound):
    """Update the values of the ecu labels."""
    tc_text = ''
    if len(car.tc_levels) > 2:
        tc_text = '{}/{}'.format(car.tc_level, len(car.tc_levels))
    ac.setText(ELECTRONIC_LABELS[38]['label_no'], tc_text)

    abs_text = ''
    if len(car.abs_levels) > 2:
        abs_text = '{}/{}'.format(car.abs_level, len(car.abs_levels))
    ac.setText(ELECTRONIC_LABELS[37]['label_no'], abs_text)

    # TODO: this should be a property for Car() and should be set when
    # .tyre_compound is set(once)
    ac.setText(ELECTRONIC_LABELS[35]['label_no'], compound or '')
    min_temp, max_temp = get_compound_temps(car.name, compound or '')
    ac.setText(ELECTRONIC_LABELS[36]['label_no'],
               "Optimum Temps: {}-{}C".format(min_temp, max_temp))
