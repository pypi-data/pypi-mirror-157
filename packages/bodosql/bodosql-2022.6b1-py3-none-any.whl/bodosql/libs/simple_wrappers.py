# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Library of wrapper functions around simple python operations
"""
import bodo


@bodo.jit
def reverse(x):
    return x[::-1]


@bodo.jit
def spaces(x):
    return x * " "
