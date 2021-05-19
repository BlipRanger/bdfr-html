import time


def float_to_datetime(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
