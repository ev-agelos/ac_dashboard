def change_car_name(car_temp):
    global CAR
    upgrades = ("_s1", "_s2", "_s3", "_drift", "_dtm")
    if car_temp.endswith(upgrades):
        upgrade = car_temp.split("_")[-1].capitalize()
        car_temp = '_'.join(car_temp.split("_")[0:-1])
    else:
        upgrade = "STD"

    if car_temp == "ktm_xbow_r":
        CAR = "X-Bow R"
    elif car_temp == "tatuusfa1":
        CAR = "Formula Abarth"
    elif car_temp == "lotus_49":
        CAR = "Type 49"
    elif car_temp == "ferrari_458":
        CAR = "458 Italia"
    elif car_temp == "bmw_z4":
        CAR = "Z4 E89 35is"
    elif car_temp == "bmw_m3_e30":
        CAR = "M3 E30 Sport Evolution"
    elif car_temp == "p4-5_2011":
        CAR = "P45 Competizione"
    elif car_temp == "abarth500":
        CAR = "500 EsseEsse"
    elif car_temp == "lotus_2_eleven":
        CAR = "2-Eleven"
    elif car_temp == "lotus_elise_sc":
        CAR = "Elise SC"
    elif car_temp in ["lotus_evora_gte", "lotus_evora_gtc"]:
        CAR = (''.join(car_temp.split("_")[1]).title() + " " +
               ''.join(car_temp.split("_")[2]).upper())
    elif car_temp == "mclaren_mp412c":
        CAR = "MP4-12C"
    elif car_temp == "mclaren_mp412c_gt3":
        CAR = "MP4-12C GT3"
    elif car_temp == "ferrari_599xxevo":
        CAR = "599xx EVO"
    elif car_temp == "bmw_m3_e30_gra":
        CAR = "M3 E30 Group A"
    elif car_temp in ["bmw_m3_gt2", "bmw_z4_gt3"]:
        CAR = ' '.join(car_temp.split("_")[1:]).upper()
    else:
        CAR = ' '.join(car_temp.split("_")[1:]).title()
    return upgrade, CAR


def change_track_name(track_temp):
    global TRACK
    if track_temp == "monza66":
        TRACK = "Monza historic 1966"
    elif track_temp == "drift":
        TRACK = "Assetto Dorifto track"
    elif "-" in track_temp:
        TRACK = ' '.join(track_temp.split("-")).title()
    else:
        TRACK = track_temp.capitalize()
    return TRACK
