# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Library of BodoSQL functions used to implement MYSQL's datetime functions
"""
import bodo
import pandas as pd


@bodo.jit
def mysql_end_of_month(ts):
    """performs a mysql LAST_DAY function"""
    return ts + pd.tseries.offsets.MonthEnd(n=0, normalize=True)


@bodo.jit
def mysql_month_diff(ts1, ts2):
    """obtains the difference in months between the two input timestamps, rounding towards 0"""
    floored_delta = (ts1.year - ts2.year) * 12 + (ts1.month - ts2.month)
    remainder = get_remainder(floored_delta, ts1, ts2)
    if floored_delta > 0 and remainder < 0:
        actual_month_delta = floored_delta - 1
    elif floored_delta < 0 and remainder > 0:
        actual_month_delta = floored_delta + 1
    else:
        actual_month_delta = floored_delta

    return -actual_month_delta


@bodo.jit
def get_remainder(month_delta, ts1, ts2):
    """helper function that returns 1 if ts1 > ts2, -1 if ts1 < ts2, and 0 if ts1 == ts2,
    ignoring the difference in month values between the two timestamps"""
    remainder = ((ts1 - pd.DateOffset(months=month_delta)) - ts2).value
    if remainder > 0:
        return 1
    elif remainder < 0:
        return -1
    else:
        return 0
