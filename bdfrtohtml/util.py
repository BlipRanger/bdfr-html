__author__ = "BlipRanger"
__version__ = "1.3.0"
__license__ = "GNU GPLv3"

import time

def float_to_datetime(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))