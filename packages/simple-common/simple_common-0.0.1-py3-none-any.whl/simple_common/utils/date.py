import time
from datetime import datetime
import pytz

shanghai_timezone = pytz.timezone('Asia/Shanghai')


def today():
    i = datetime.now(pytz.timezone('Asia/Shanghai'))
    return i.strftime("%Y_%m_%d")


def time_now(time_format='%H%M%S'):
    i = datetime.now(pytz.timezone('Asia/Shanghai'))
    return i.strftime(time_format)


def now():
    return datetime.now(pytz.timezone('Asia/Shanghai'))


def millisecond_unix():
    t = time.time()
    return int(round(t * 1000))


def now_str():
    i = datetime.now(shanghai_timezone)
    time_format = "%Y%m%d_%H%M%S"
    return i.strftime(time_format)


def today_str():
    i = datetime.now(pytz.timezone('Asia/Shanghai'))
    return i.strftime("%Y_%m_%d")


def time_now_str(time_format='%H%M%S'):
    i = datetime.now(pytz.timezone('Asia/Shanghai'))
    return i.strftime(time_format)
