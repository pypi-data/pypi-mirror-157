
# Copyright (C) 2021 Bodo Inc. All rights reserved.
""" There are a large number of operators that need a wrapper that returns null if any of the input arguments are null,
and otherwise return the result of the original function. This file is an automatically generated file, that contains
these library functions.
DO NOT MANUALLY CHANGE THIS FILE!
"""
import bodosql
import bodo
import operator
import numpy as np
import pandas as pd
import re
from numba import generated_jit


@generated_jit(nopython=True)
def sql_null_checking_not(arg0):
    "automatically generated library function for not"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return not(arg0)
        return impl

    else:
        return lambda arg0: not(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_addition(arg0, arg1):
    "automatically generated library function for addition"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.add(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.add(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_subtraction(arg0, arg1):
    "automatically generated library function for subtraction"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.sub(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.sub(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_multiplication(arg0, arg1):
    "automatically generated library function for multiplication"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.mul(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.mul(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_true_division(arg0, arg1):
    "automatically generated library function for true_division"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return np.true_divide(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: np.true_divide(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_modulo(arg0, arg1):
    "automatically generated library function for modulo"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return np.mod(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: np.mod(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_power(arg0, arg1):
    "automatically generated library function for power"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.pow(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.pow(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_equal(arg0, arg1):
    "automatically generated library function for equal"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.eq(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.eq(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_not_equal(arg0, arg1):
    "automatically generated library function for not_equal"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.ne(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.ne(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_less_than(arg0, arg1):
    "automatically generated library function for less_than"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.lt(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.lt(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_less_than_or_equal(arg0, arg1):
    "automatically generated library function for less_than_or_equal"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.le(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.le(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_greater_than(arg0, arg1):
    "automatically generated library function for greater_than"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.gt(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.gt(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_greater_than_or_equal(arg0, arg1):
    "automatically generated library function for greater_than_or_equal"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return operator.ge(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: operator.ge(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_rpad_scalar(arg0, arg1, arg2):
    "automatically generated library function for rpad_scalar"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none or arg2 == bodo.none):
        return lambda arg0, arg1, arg2: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional) or isinstance(arg2, bodo.optional)):
        def impl(arg0, arg1, arg2):
            if (arg0 is None or arg1 is None or arg2 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                arg2 = bodo.utils.indexing.unoptional(arg2)
                return bodosql.libs.LR_pad_string.rpad_scalar(arg0, arg1, arg2)
        return impl

    else:
        return lambda arg0, arg1, arg2: bodosql.libs.LR_pad_string.rpad_scalar(arg0, arg1, arg2)
        

@generated_jit(nopython=True)
def sql_null_checking_lpad_scalar(arg0, arg1, arg2):
    "automatically generated library function for lpad_scalar"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none or arg2 == bodo.none):
        return lambda arg0, arg1, arg2: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional) or isinstance(arg2, bodo.optional)):
        def impl(arg0, arg1, arg2):
            if (arg0 is None or arg1 is None or arg2 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                arg2 = bodo.utils.indexing.unoptional(arg2)
                return bodosql.libs.LR_pad_string.lpad_scalar(arg0, arg1, arg2)
        return impl

    else:
        return lambda arg0, arg1, arg2: bodosql.libs.LR_pad_string.lpad_scalar(arg0, arg1, arg2)
        

@generated_jit(nopython=True)
def sql_null_checking_conv_scalar(arg0, arg1, arg2):
    "automatically generated library function for conv_scalar"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none or arg2 == bodo.none):
        return lambda arg0, arg1, arg2: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional) or isinstance(arg2, bodo.optional)):
        def impl(arg0, arg1, arg2):
            if (arg0 is None or arg1 is None or arg2 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                arg2 = bodo.utils.indexing.unoptional(arg2)
                return bodosql.libs.numeric_helpers.conv_scalar(arg0, arg1, arg2)
        return impl

    else:
        return lambda arg0, arg1, arg2: bodosql.libs.numeric_helpers.conv_scalar(arg0, arg1, arg2)
        

@generated_jit(nopython=True)
def sql_null_checking_sql_to_python(arg0):
    "automatically generated library function for sql_to_python"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.regex.sql_to_python(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.regex.sql_to_python(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_ord_scalar(arg0):
    "automatically generated library function for ord_scalar"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.string_helpers.bodosql_ord_scalar(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.string_helpers.bodosql_ord_scalar(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_chr_scalar(arg0):
    "automatically generated library function for chr_scalar"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.string_helpers.bodosql_chr_scalar(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.string_helpers.bodosql_chr_scalar(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_substr_scalar(arg0, arg1, arg2):
    "automatically generated library function for substr_scalar"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none or arg2 == bodo.none):
        return lambda arg0, arg1, arg2: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional) or isinstance(arg2, bodo.optional)):
        def impl(arg0, arg1, arg2):
            if (arg0 is None or arg1 is None or arg2 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                arg2 = bodo.utils.indexing.unoptional(arg2)
                return bodosql.libs.substring_helper.mysql_substr_scalar(arg0, arg1, arg2)
        return impl

    else:
        return lambda arg0, arg1, arg2: bodosql.libs.substring_helper.mysql_substr_scalar(arg0, arg1, arg2)
        

@generated_jit(nopython=True)
def sql_null_checking_substr_index_scalar(arg0, arg1, arg2):
    "automatically generated library function for substr_index_scalar"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none or arg2 == bodo.none):
        return lambda arg0, arg1, arg2: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional) or isinstance(arg2, bodo.optional)):
        def impl(arg0, arg1, arg2):
            if (arg0 is None or arg1 is None or arg2 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                arg2 = bodo.utils.indexing.unoptional(arg2)
                return bodosql.libs.substring_helper.mysql_substr_index_scalar(arg0, arg1, arg2)
        return impl

    else:
        return lambda arg0, arg1, arg2: bodosql.libs.substring_helper.mysql_substr_index_scalar(arg0, arg1, arg2)
        

@generated_jit(nopython=True)
def sql_null_checking_mysql_instr(arg0, arg1):
    "automatically generated library function for mysql_instr"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return bodosql.libs.two_op_string_fn_helpers.mysql_instr(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: bodosql.libs.two_op_string_fn_helpers.mysql_instr(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_mysql_strcmp(arg0, arg1):
    "automatically generated library function for mysql_strcmp"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return bodosql.libs.two_op_string_fn_helpers.mysql_strcmp(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: bodosql.libs.two_op_string_fn_helpers.mysql_strcmp(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_mysql_right(arg0, arg1):
    "automatically generated library function for mysql_right"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return bodosql.libs.two_op_string_fn_helpers.mysql_right(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: bodosql.libs.two_op_string_fn_helpers.mysql_right(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_mysql_left(arg0, arg1):
    "automatically generated library function for mysql_left"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return bodosql.libs.two_op_string_fn_helpers.mysql_left(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: bodosql.libs.two_op_string_fn_helpers.mysql_left(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_strip(arg0, arg1):
    "automatically generated library function for strip"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return arg0.strip(arg1)
        return impl

    else:
        return lambda arg0, arg1: arg0.strip(arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_lstrip(arg0, arg1):
    "automatically generated library function for lstrip"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return arg0.lstrip(arg1)
        return impl

    else:
        return lambda arg0, arg1: arg0.lstrip(arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_rstrip(arg0, arg1):
    "automatically generated library function for rstrip"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return arg0.rstrip(arg1)
        return impl

    else:
        return lambda arg0, arg1: arg0.rstrip(arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_len(arg0):
    "automatically generated library function for len"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return len(arg0)
        return impl

    else:
        return lambda arg0: len(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_upper(arg0):
    "automatically generated library function for upper"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.upper()
        return impl

    else:
        return lambda arg0: arg0.upper()
        

@generated_jit(nopython=True)
def sql_null_checking_lower(arg0):
    "automatically generated library function for lower"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.lower()
        return impl

    else:
        return lambda arg0: arg0.lower()
        

@generated_jit(nopython=True)
def sql_null_checking_replace(arg0, arg1, arg2):
    "automatically generated library function for replace"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none or arg2 == bodo.none):
        return lambda arg0, arg1, arg2: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional) or isinstance(arg2, bodo.optional)):
        def impl(arg0, arg1, arg2):
            if (arg0 is None or arg1 is None or arg2 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                arg2 = bodo.utils.indexing.unoptional(arg2)
                return arg0.replace(arg1, arg2)
        return impl

    else:
        return lambda arg0, arg1, arg2: arg0.replace(arg1, arg2)
        

@generated_jit(nopython=True)
def sql_null_checking_spaces(arg0):
    "automatically generated library function for spaces"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.simple_wrappers.spaces(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.simple_wrappers.spaces(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_reverse(arg0):
    "automatically generated library function for reverse"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.simple_wrappers.reverse(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.simple_wrappers.reverse(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_negate(arg0):
    "automatically generated library function for negate"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return operator.neg(arg0)
        return impl

    else:
        return lambda arg0: operator.neg(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_in(arg0, arg1):
    "automatically generated library function for in"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return (arg0 in arg1)
        return impl

    else:
        return lambda arg0, arg1: (arg0 in arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_re_match(arg0, arg1):
    "automatically generated library function for re_match"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return bool(re.match(arg0, arg1))
        return impl

    else:
        return lambda arg0, arg1: bool(re.match(arg0, arg1))
        

@generated_jit(nopython=True)
def sql_null_checking_timestamp_dayfloor(arg0):
    "automatically generated library function for timestamp_dayfloor"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.floor(freq='D')
        return impl

    else:
        return lambda arg0: arg0.floor(freq='D')
        

@generated_jit(nopython=True)
def sql_null_checking_strftime(arg0, arg1):
    "automatically generated library function for strftime"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return arg0.strftime(arg1)
        return impl

    else:
        return lambda arg0, arg1: arg0.strftime(arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_pd_to_datetime_with_format(arg0, arg1):
    "automatically generated library function for pd_to_datetime_with_format"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return bodosql.libs.datetime_wrappers.pd_to_datetime_with_format(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: bodosql.libs.datetime_wrappers.pd_to_datetime_with_format(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_pd_Timestamp_single_value(arg0):
    "automatically generated library function for pd_Timestamp_single_value"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.datetime_wrappers.pd_Timestamp_single_value(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.datetime_wrappers.pd_Timestamp_single_value(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_pd_Timestamp_single_value_with_second_unit(arg0):
    "automatically generated library function for pd_Timestamp_single_value_with_second_unit"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.datetime_wrappers.pd_Timestamp_single_value_with_second_unit(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.datetime_wrappers.pd_Timestamp_single_value_with_second_unit(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_pd_Timestamp_single_value_with_day_unit(arg0):
    "automatically generated library function for pd_Timestamp_single_value_with_day_unit"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.datetime_wrappers.pd_Timestamp_single_value_with_day_unit(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.datetime_wrappers.pd_Timestamp_single_value_with_day_unit(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_pd_Timestamp_single_value_with_year_unit(arg0):
    "automatically generated library function for pd_Timestamp_single_value_with_year_unit"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.datetime_wrappers.pd_Timestamp_single_value_with_year_unit(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.datetime_wrappers.pd_Timestamp_single_value_with_year_unit(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_pd_Timestamp_y_m_d(arg0, arg1, arg2):
    "automatically generated library function for pd_Timestamp_y_m_d"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none or arg2 == bodo.none):
        return lambda arg0, arg1, arg2: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional) or isinstance(arg2, bodo.optional)):
        def impl(arg0, arg1, arg2):
            if (arg0 is None or arg1 is None or arg2 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                arg2 = bodo.utils.indexing.unoptional(arg2)
                return bodosql.libs.datetime_wrappers.pd_Timestamp_y_m_d(arg0, arg1, arg2)
        return impl

    else:
        return lambda arg0, arg1, arg2: bodosql.libs.datetime_wrappers.pd_Timestamp_y_m_d(arg0, arg1, arg2)
        

@generated_jit(nopython=True)
def sql_null_checking_pd_timedelta_days(arg0):
    "automatically generated library function for pd_timedelta_days"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.days
        return impl

    else:
        return lambda arg0: arg0.days
        

@generated_jit(nopython=True)
def sql_null_checking_pd_timedelta_total_seconds(arg0):
    "automatically generated library function for pd_timedelta_total_seconds"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.total_seconds()
        return impl

    else:
        return lambda arg0: arg0.total_seconds()
        

@generated_jit(nopython=True)
def sql_null_checking_yearofweek(arg0):
    "automatically generated library function for yearofweek"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.isocalendar()[0]
        return impl

    else:
        return lambda arg0: arg0.isocalendar()[0]
        

@generated_jit(nopython=True)
def sql_null_checking_weekofyear(arg0):
    "automatically generated library function for weekofyear"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.weekofyear
        return impl

    else:
        return lambda arg0: arg0.weekofyear
        

@generated_jit(nopython=True)
def sql_null_checking_dayofyear(arg0):
    "automatically generated library function for dayofyear"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.dayofyear
        return impl

    else:
        return lambda arg0: arg0.dayofyear
        

@generated_jit(nopython=True)
def sql_null_checking_microsecond(arg0):
    "automatically generated library function for microsecond"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.microsecond
        return impl

    else:
        return lambda arg0: arg0.microsecond
        

@generated_jit(nopython=True)
def sql_null_checking_second(arg0):
    "automatically generated library function for second"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.second
        return impl

    else:
        return lambda arg0: arg0.second
        

@generated_jit(nopython=True)
def sql_null_checking_minute(arg0):
    "automatically generated library function for minute"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.minute
        return impl

    else:
        return lambda arg0: arg0.minute
        

@generated_jit(nopython=True)
def sql_null_checking_hour(arg0):
    "automatically generated library function for hour"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.hour
        return impl

    else:
        return lambda arg0: arg0.hour
        

@generated_jit(nopython=True)
def sql_null_checking_day(arg0):
    "automatically generated library function for day"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.day
        return impl

    else:
        return lambda arg0: arg0.day
        

@generated_jit(nopython=True)
def sql_null_checking_month(arg0):
    "automatically generated library function for month"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.month
        return impl

    else:
        return lambda arg0: arg0.month
        

@generated_jit(nopython=True)
def sql_null_checking_quarter(arg0):
    "automatically generated library function for quarter"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.quarter
        return impl

    else:
        return lambda arg0: arg0.quarter
        

@generated_jit(nopython=True)
def sql_null_checking_year(arg0):
    "automatically generated library function for year"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return arg0.year
        return impl

    else:
        return lambda arg0: arg0.year
        

@generated_jit(nopython=True)
def sql_null_checking_dayofweek(arg0):
    "automatically generated library function for dayofweek"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return bodosql.libs.datetime_wrappers.sql_dow(arg0)
        return impl

    else:
        return lambda arg0: bodosql.libs.datetime_wrappers.sql_dow(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_ceil(arg0):
    "automatically generated library function for ceil"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.ceil(arg0)
        return impl

    else:
        return lambda arg0: np.ceil(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_floor(arg0):
    "automatically generated library function for floor"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.floor(arg0)
        return impl

    else:
        return lambda arg0: np.floor(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_mod(arg0, arg1):
    "automatically generated library function for mod"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return np.mod(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: np.mod(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_sign(arg0):
    "automatically generated library function for sign"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.sign(arg0)
        return impl

    else:
        return lambda arg0: np.sign(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_round(arg0, arg1):
    "automatically generated library function for round"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return round(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: round(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_abs(arg0):
    "automatically generated library function for abs"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return abs(arg0)
        return impl

    else:
        return lambda arg0: abs(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_log2(arg0):
    "automatically generated library function for log2"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.log2(arg0)
        return impl

    else:
        return lambda arg0: np.log2(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_log10(arg0):
    "automatically generated library function for log10"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.log10(arg0)
        return impl

    else:
        return lambda arg0: np.log10(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_ln(arg0):
    "automatically generated library function for ln"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.log(arg0)
        return impl

    else:
        return lambda arg0: np.log(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_exp(arg0):
    "automatically generated library function for exp"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.exp(arg0)
        return impl

    else:
        return lambda arg0: np.exp(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_pow(arg0, arg1):
    "automatically generated library function for pow"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return pow(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: pow(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_arccos(arg0):
    "automatically generated library function for arccos"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.arccos(arg0)
        return impl

    else:
        return lambda arg0: np.arccos(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_arcsin(arg0):
    "automatically generated library function for arcsin"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.arcsin(arg0)
        return impl

    else:
        return lambda arg0: np.arcsin(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_arctan(arg0):
    "automatically generated library function for arctan"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.arctan(arg0)
        return impl

    else:
        return lambda arg0: np.arctan(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_arctan2(arg0, arg1):
    "automatically generated library function for arctan2"

    #if either input is None, return None
    if (arg0 == bodo.none or arg1 == bodo.none):
        return lambda arg0, arg1: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional) or isinstance(arg1, bodo.optional)):
        def impl(arg0, arg1):
            if (arg0 is None or arg1 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                arg1 = bodo.utils.indexing.unoptional(arg1)
                return np.arctan2(arg0, arg1)
        return impl

    else:
        return lambda arg0, arg1: np.arctan2(arg0, arg1)
        

@generated_jit(nopython=True)
def sql_null_checking_cos(arg0):
    "automatically generated library function for cos"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.cos(arg0)
        return impl

    else:
        return lambda arg0: np.cos(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_sin(arg0):
    "automatically generated library function for sin"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.sin(arg0)
        return impl

    else:
        return lambda arg0: np.sin(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_tan(arg0):
    "automatically generated library function for tan"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.tan(arg0)
        return impl

    else:
        return lambda arg0: np.tan(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_radians(arg0):
    "automatically generated library function for radians"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.radians(arg0)
        return impl

    else:
        return lambda arg0: np.radians(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_degrees(arg0):
    "automatically generated library function for degrees"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.degrees(arg0)
        return impl

    else:
        return lambda arg0: np.degrees(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_scalar_conv_bool(arg0):
    "automatically generated library function for scalar_conv_bool"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.bool_(arg0)
        return impl

    else:
        return lambda arg0: np.bool_(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_scalar_conv_int8(arg0):
    "automatically generated library function for scalar_conv_int8"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.int8(arg0)
        return impl

    else:
        return lambda arg0: np.int8(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_scalar_conv_int16(arg0):
    "automatically generated library function for scalar_conv_int16"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.int16(arg0)
        return impl

    else:
        return lambda arg0: np.int16(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_scalar_conv_int32(arg0):
    "automatically generated library function for scalar_conv_int32"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.int32(arg0)
        return impl

    else:
        return lambda arg0: np.int32(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_scalar_conv_int64(arg0):
    "automatically generated library function for scalar_conv_int64"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return np.int64(arg0)
        return impl

    else:
        return lambda arg0: np.int64(arg0)
        

@generated_jit(nopython=True)
def sql_null_checking_scalar_conv_str(arg0):
    "automatically generated library function for scalar_conv_str"

    #if either input is None, return None
    if (arg0 == bodo.none):
        return lambda arg0: None

    # If either input is optional, the output is optional.
    # We could merge this code path with the default, but
    # if we can avoid optional types we should.
    elif (isinstance(arg0, bodo.optional)):
        def impl(arg0):
            if (arg0 is None):
                return None
            else:
                # Call internal bodo function that changes the converts the
                # type of Optional(type) to just type. If a or b isn't optional
                # this is basically a noop
                arg0 = bodo.utils.indexing.unoptional(arg0)
                return str(arg0)
        return impl

    else:
        return lambda arg0: str(arg0)
        