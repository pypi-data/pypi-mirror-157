# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Library of BodoSQL functions used to support string builtin functions
"""
import bodo


@bodo.jit
def bodosql_ord_scalar(input_string):
    """performs a checked ord"""
    if len(input_string) == 0:
        # default MYSQL behavior on empty string is to return 0
        return 0
    else:
        return ord(input_string[0])


@bodo.jit
def bodosql_chr_scalar(input_int):
    """performs a checked chr. Checks for nulls"""
    # TODO: allow returning more then ascii characters
    if input_int < 0 or input_int > 127:
        return None
    else:
        return chr(input_int)
