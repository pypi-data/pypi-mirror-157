# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Library of BodoSQL functions that wrap datetime functions with named arguments
"""
import bodo
import pandas as pd


@bodo.jit
def pd_to_datetime_with_format(s, my_format):
    return pd.to_datetime(s, format=my_format)


@bodo.jit
def pd_Timestamp_single_value(v):
    return pd.Timestamp(v)


# Currently, these cannot be seperate functions. This is due to the fact that the unit argument
# must be litteral. However, if the unit argument is converted to optional type, it seems that
# the fact that it is litteral is lost.
@bodo.jit
def pd_Timestamp_single_value_with_day_unit(v):
    return pd.Timestamp(v, unit="D")


@bodo.jit
def pd_Timestamp_single_value_with_year_unit(v):
    return pd.Timestamp(v, unit="Y")


@bodo.jit
def pd_Timestamp_single_value_with_second_unit(v):
    return pd.Timestamp(v, unit="s")


@bodo.jit
def pd_Timestamp_y_m_d(y, m, d):
    return pd.Timestamp(year=y, month=m, day=d)


@bodo.jit
def sql_dow(x):
    return (x.dayofweek + 1) % 7 + 1
