# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
Test correctness of bodosql.libs.substring_helper functions
"""
import pandas as pd
import pytest

import bodosql


@pytest.fixture(
    params=[
        ("", "", 2, ""),
        ("hello wolrd", "", 1, ""),
        ("h ello w orld", " ", 3, "h ello w"),
        ("h ello w orld", " ", 0, ""),
        ("h ello w orld", " ", -2, "w orld"),
        ('h ." ."ello world', '."', 2, 'h ." '),
    ]
)
def substr_index_inputs_scalar(request):
    """Fixture that returns a quadrople of values.
    1-3 are the inputs to mysql_substr_index_scalar, and the 4th is the expected output"""
    return request.param


@pytest.fixture(
    params=[
        (0, 0, 0, 0),
        (2, 0, 0, 0),
        (1, 2, 0, 2),
        (2, 4, 1, 5),
        (-1, 4, -1, None),
        (-4, 4, -4, None),
        (-4, 1, -4, -3),
        (-4, 0, -4, -4),
    ]
)
def substr_slice_inputs_cols(request):
    """Fixture that returns a quadruple of integers.
    first two integers are the arguments to mysql_substr, the second two are the arguments for str.slice,
    such that you get on equivalent output"""
    return request.param


@pytest.fixture(
    params=[
        ("", 1, 2, ""),
        ("hello world", 0, 4, ""),
        ("hello world", 2, 0, ""),
        ("hello world", 4, 3, "lo "),
        ("hello world", 4, -1, ""),
        ("hello world", -4, 3, "orl"),
        ("hello world", -4, 20, "orld"),
        ("hello world", -4, 0, ""),
    ]
)
def substr_inputs_scalar(request):
    """Fixture that returns a quadruple of values.
    1-3 are the inputs to mysql_substr_columns, and the 4th is the expected output"""
    return request.param


@pytest.mark.slow
def test_substring_columns(bodosql_string_types, substr_slice_inputs_cols):
    """tests that bodosql.libs.substring_helper.mysql_substr_col_arg0 is behaving correctly"""
    substr_arg1 = substr_slice_inputs_cols[0]
    substr_arg2 = substr_slice_inputs_cols[1]
    slice_arg1 = substr_slice_inputs_cols[2]
    slice_arg2 = substr_slice_inputs_cols[3]

    for col in ["A", "B", "C"]:
        pd.testing.assert_series_equal(
            bodosql.libs.substring_helper.mysql_substr_col_arg0(
                bodosql_string_types["table1"][col], substr_arg1, substr_arg2
            ),
            bodosql_string_types["table1"][col].str.slice(slice_arg1, slice_arg2),
        )


@pytest.mark.slow
def test_substring_scalar(substr_inputs_scalar):
    """tests that bodosql.libs.substring_helper.mysql_substr_scalar is behaving correctly"""
    arg1 = substr_inputs_scalar[0]
    arg2 = substr_inputs_scalar[1]
    arg3 = substr_inputs_scalar[2]
    output = substr_inputs_scalar[3]

    assert bodosql.libs.substring_helper.mysql_substr_scalar(arg1, arg2, arg3) == output


@pytest.mark.slow
def test_substring_index_scalar(substr_index_inputs_scalar):
    """tests that bodosql.libs.substring_helper.mysql_substr_index_scalar is behaving correctly"""
    arg1 = substr_index_inputs_scalar[0]
    arg2 = substr_index_inputs_scalar[1]
    arg3 = substr_index_inputs_scalar[2]
    output = substr_index_inputs_scalar[3]

    assert (
        bodosql.libs.substring_helper.mysql_substr_index_scalar(arg1, arg2, arg3)
        == output
    )
