#!/usr/bin/env python3

import gc
import re
from datetime import datetime
import timeit
from pymonetdb.exceptions import OperationalError
from pymonetdb.sql.pythonize import py_timestamp

PATTERN = re.compile('(?a)(\d+)-(\d\d)-(\d\d) (\d+):(\d\d):(\d\d)(?:[.](\d*))?')


def re_timestamp(t):
    m = PATTERN.match(t)
    if m:
        return datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6]), int(((m.group(7) or '') + '000000')[:6]))
    else:
        raise OperationalError(f"invalid date: {t}")


def split_timestamp(t):
    date_part, time_part = t.split(' ', 2)
    year, month, day = date_part.split('-', 3)
    hour, min, sec_usec = time_part.split(':', 3)
    sec_parts = sec_usec.split('.', 2)
    sec = sec_parts[0]
    if len(sec_parts) == 2:
        usec = int((sec_parts[1] + '000000')[:6])
    else:
        usec = 0
    return datetime(int(year), int(month), int(day), int(hour), int(min), int(sec), usec)


dates = ['2015-02-14 20:50:12.34' for i in range(10_000)]


def bench_py_timestamp():
    return [py_timestamp(t) for t in dates]


def bench_re_timestamp():
    return [re_timestamp(t) for t in dates]


def bench_split_timestamp():
    return [split_timestamp(t) for t in dates]

# timer_baseline = timeit.Timer('bench_py_timestamp()', globals=globals())
# print('baseline', timer_baseline.autorange()[1])

# timer_re = timeit.Timer('bench_re_timestamp()', globals=globals())
# print('re', timer_re.autorange()[1])


# timer_baseline = timeit.Timer('bench_py_timestamp()', globals=globals())
# print('baseline', timer_baseline.autorange()[1])

# timer_re = timeit.Timer('bench_re_timestamp()', globals=globals())
# print('re', timer_re.autorange()[1])

for testcase in ['bench_py_timestamp()', 'bench_re_timestamp()', 'bench_split_timestamp()']:
    timer = timeit.Timer(testcase, globals=globals())
    tmin = 1e99
    for i in range(10):
        gc.collect()
        t = timer.autorange()[1]
        tmin = min(t, tmin)
    print(testcase, tmin)


