# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Helper functions for dealing with the mysql Substring operation

    MYSQL substring syntax is as follows:
    substring(string, start, len)
    Start = 0 means return emptystring. Start = 1 means start at the first char
    Start = -x means start at len(str) -x. If len(str) < abs(x), return empty string
    If the length is negative, return empty string
    string, start, and len can be either scalars or columns

    pandas str.slice behavior is as follows
    slice(start, end) (star incl, end not incl)
    pd.str.slice behavior is the same as str[start:end] on a scalar
    Start = 0 means start at the first char
    start and end can both be negative, and results in end/start = len(str) - x
    if start or end abs(start/end) > len(string) and start/end are negative, return empty string

    The functions in this file perform the transformation from the substring syntax,
    to the equivalent python slicing syntax.
"""
import bodo
import pandas as pd


@bodo.jit
def mysql_substr_scalar(input_str, substr_start, substr_len):
    """Takes scalar arguments to a mysql substring call, and uses
    python slicing to perform an equivalent operation
    """
    if substr_start == 0 or substr_len < 0:
        result = ""
    elif substr_start >= 1:
        # start and len are both positive
        result = input_str[substr_start - 1 : substr_start - 1 + substr_len]
    else:
        # start is negative, len is positive
        # By w3 Mysql, in the case that the absolute value of start is greater then the length of the string,
        # you should return "", but it seems that spark returns the whole string.
        # for right now, I'm choosing to return the whole string.
        diff = substr_start + substr_len
        if (diff) >= 0:
            # if the length is larger then the number of index, slice everything off the end
            result = input_str[substr_start:]
        else:
            result = input_str[substr_start:diff]
    return result


# In order for this to work, we need support for the possibly distributed flag for the column input
# see BS-386, BE-952, and BE-953
@bodo.jit
def mysql_substr_col_arg0(column, substr_start, substr_len):
    """Helper function that can be called in the case we have a substring call with a column arg0, and scalar arg1/2's"""
    if substr_start == 0 or substr_len < 0:
        return column.str.slice(0, 0)
    elif substr_start >= 1:
        # start and len are both positive
        return column.str.slice(substr_start - 1, substr_start - 1 + substr_len)
    else:
        # start is negative, len is positive
        diff = substr_start + substr_len
        if (diff) >= 0:
            # if the length is larger then the number of index, slice everything off the end
            return column.str.slice(substr_start)
        else:
            return column.str.slice(substr_start, diff)


@bodo.jit
def mysql_substr_index_scalar(base_string, delimiter_string, num_occurrences):
    """Helper function that pefroms a substring_index operation on scalar values"""
    if pd.isna(base_string) or pd.isna(delimiter_string) or pd.isna(num_occurrences):
        return None
    elif delimiter_string == "":
        return ""
    elif num_occurrences >= 0:
        return delimiter_string.join(
            base_string.split(delimiter_string, num_occurrences + 1)[0:num_occurrences]
        )
    else:
        return delimiter_string.join(
            base_string.split(delimiter_string)[num_occurrences:]
        )
