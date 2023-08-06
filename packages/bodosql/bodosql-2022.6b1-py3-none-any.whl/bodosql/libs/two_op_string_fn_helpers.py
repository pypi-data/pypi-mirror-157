# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Library of BodoSQL functions used to support
    Two argument string function
"""
import bodo


@bodo.jit
def mysql_instr(base_string, string_to_search_for):
    """
    pefroms a mysql instr call on two scalar strings
    INSTR returns 0 on failure, and returns the index of the first occurance plus one
    find returns -1 on failure, and returns the index of the first occurance
    """
    res = base_string.find(string_to_search_for)
    if res == -1:
        return 0
    else:
        return res + 1


@bodo.jit
def mysql_strcmp(str1, str2):
    """
    performs a mysql str compare on the two scalar strings
    """
    if str1 > str2:
        return 1
    elif str2 > str1:
        return -1
    else:
        return 0


# again, we could have a function that does a series.str.slice on a column input to avoid an apply,
# pending the addition of a possibly distributed flag


@bodo.jit
def mysql_right(input_str, num):
    if num <= 0:
        return ""
    else:
        return input_str[-num:]


@bodo.jit
def mysql_left(input_str, num):
    if num <= 0:
        return ""
    else:
        return input_str[:num]
