import datetime


def int_to_time(int_number):
    temptime = datetime.timedelta(milliseconds=int_number)
    minutes = temptime.seconds // 60
    seconds = temptime.seconds % 60
    milliseconds = round(temptime.microseconds / 1000)
    if milliseconds < 100:
        milliseconds = milliseconds / 1000
        if seconds < 10:
            return str(minutes) + ":0" + str(seconds + milliseconds)
        else:
            return str(minutes) + ":" + str(seconds + milliseconds)
    else:
        if seconds < 10:
            return str(minutes) + ":0" + str(seconds) + "." + str(milliseconds)
        else:
            return str(minutes) + ":" + str(seconds) + "." + str(milliseconds)
