# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Library of BodoSQL functions used for performing L/R pad operations. Unfortunately,
    the equivalent pandas/python functions can only pad with a single length characters,
    so we have to use a custom scalar function to emulate MySQL behavior.

    #https://www.w3schools.com/sql/trymysql.asp?filename=trysql_func_mysql_lpad
    
    If the length is less then the length of the base string, it truncates it.
    If the pad string padding is empty string, and padding needs to occur, it returns
    empty string.

    Not currently wrapping these with a null check, as it will most likely be possible
    to generate a null check wrapper automatically in the future

"""
import bodo


@bodo.jit
def rpad_scalar(base_string, length, pad_string):
    """performs a mysql rpad"""
    if len(base_string) >= length:
        return base_string[:length]
    elif len(pad_string) == 0:
        return ""
    padding = extend_string(pad_string, length - len(base_string))

    return base_string + padding


@bodo.jit
def lpad_scalar(base_string, length, pad_string):
    """performs a mysql lpad"""
    if len(base_string) >= length:
        return base_string[:length]
    elif len(pad_string) == 0:
        return ""

    padding = extend_string(pad_string, length - len(base_string))
    return padding + base_string


@bodo.jit
def extend_string(string, length):
    """returns the string, extended to the specified length by repeating it"""
    divisor = (length) // len(string)
    quotient = (length) % len(string)

    return string * divisor + string[:quotient]
