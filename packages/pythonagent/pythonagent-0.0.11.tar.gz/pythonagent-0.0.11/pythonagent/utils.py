import time


def get_current_timestamp_in_ms():
    try :
        time_stamp = time.time_ns() // 1000000
    except Exception as e:
        time_stamp = time.time()*1000

    return time_stamp

