# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Library of BodoSQL functions used to support numeric builtin functions
"""
import bodo


@bodo.jit
def conv_scalar(val, current_base, converted_base):
    base_map = {2: "{0:b}", 8: "{0:o}", 10: "{0:d}", 16: "{0:x}"}
    new_format = base_map[converted_base]
    return new_format.format(int(val, current_base))
