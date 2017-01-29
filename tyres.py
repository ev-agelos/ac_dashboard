TYRE_COMPS = {
    'Street': (75, 85),
    'Semislicks': (75, 100),
    # GT2
    'Slick SuperSoft': (90, 105),
    'Slick Soft': (90, 105),
    'Slick Medium': (85, 105),
    'Slick Hard': (80, 100),
    'Slick SuperHard': (80, 100),
    # GT3
    'Slicks Soft': (80, 110),
    'Slicks Medium': (75, 105),
    'Slicks Hard': (70, 100),
    'F1 1967': (50, 90),
    'Slicks Soft Gr.A': (0, 0),
    'Slicks Medium gr.A': (0, 0),
    'Slicks Hard gr.A': (0, 0),
    'Slicks Soft DTM90s': (0, 0),
    'Slicks Medium DTM90s': (0, 0),
    'Slicks Hard DTM90s': (0, 0),
    'Street90S': (0, 0),
    'Street 90s': (0, 0),
    'Trofeo Slicks': (0, 0),
    'Soft 70F1': (50, 90),
    'Hard 70F1': (50, 90),
    'Slick Exos': (90, 120),
    'TopGear Record': (0, 0)
}
EXOS_TYRE_COMPS = {'Slick SuperSoft': (85, 110), 'Slick Soft': (105, 125),
                   'Slick Medium': (90, 115), 'Slick Hard': (110, 135)}


def get_compound_temps(car_name, compound):
    """Return the optimum temp range of the <compound>."""
    tyre_temps = TYRE_COMPS
    if car_name == "lotus_exos_125_s1":
        tyre_temps = EXOS_TYRE_COMPS
    return tyre_temps.get(compound, (0, 0))