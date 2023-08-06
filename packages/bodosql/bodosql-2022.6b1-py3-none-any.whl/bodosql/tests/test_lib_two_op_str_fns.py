# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Tests the functions used to support
    Two argument string function
"""
import pytest

import bodosql


@pytest.fixture(
    params=[
        (("hello world", "e"), 2),
        (("", "e"), 0),
        (("e", "e"), 1),
        (("falalala", "la"), 3),
        (("e", "la"), 0),
        (("abcedfg", "g"), 7),
    ]
)
def instr_info(request):
    """tuple containing the inputs to a mysql instr operation, and the expected output"""
    return request.param


@pytest.mark.slow
def test_mysql_instr(instr_info):
    """tests the library implementation of instr"""
    args = instr_info[0]
    retval = instr_info[1]
    assert bodosql.libs.two_op_string_fn_helpers.mysql_instr(args[0], args[1]) == retval


@pytest.fixture(
    params=[((chr(x), chr(x + 1)), -1) for x in [0, 125, 17]]
    + [((chr(x + 1), chr(x)), 1) for x in [0, 125, 102]]
    + [((chr(x), chr(x)), 0) for x in [0, 127, 24]]
    + [((chr(x) + "abcdefg", chr(x)), 1) for x in [0, 127, 7]]
)
def strcmp_info(request):
    """tuple containing the inputs to a mysql strcmp operation, and the expected output"""
    return request.param


@pytest.mark.slow
def test_strcmp(strcmp_info):
    """tests the library implementation of strcmp"""
    args = strcmp_info[0]
    retval = strcmp_info[1]
    assert (
        bodosql.libs.two_op_string_fn_helpers.mysql_strcmp(args[0], args[1]) == retval
    )


@pytest.mark.slow
def test_left_right():
    """tests the library implementation of left/right"""

    strings = ["hello world", "asdgasdfasd", "////%%%%%%%", "", "e"]
    valid_lengths = [1, 5, 12412]
    invalid_lengths = [-1, 0, -1231]

    for cur_str in strings:
        for val_len in valid_lengths:
            assert (
                bodosql.libs.two_op_string_fn_helpers.mysql_right(cur_str, val_len)
                == cur_str[-val_len:]
            )
            assert (
                bodosql.libs.two_op_string_fn_helpers.mysql_left(cur_str, val_len)
                == cur_str[:val_len]
            )
        for inval_len in invalid_lengths:
            assert (
                bodosql.libs.two_op_string_fn_helpers.mysql_right(cur_str, inval_len)
                == ""
            )
            assert (
                bodosql.libs.two_op_string_fn_helpers.mysql_left(cur_str, inval_len)
                == ""
            )
