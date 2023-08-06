# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
    Tests the library of BodoSQL functions used to implement MYSQL's datetime functions
"""
import pandas as pd
import pytest

import bodosql


@pytest.fixture(
    params=[
        (pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-31")),
        (pd.Timestamp("2024-02-12"), pd.Timestamp("2024-02-29")),
        (pd.Timestamp("2005-02-02"), pd.Timestamp("2005-02-28")),
        (pd.Timestamp("1970-11-12 12:02:13.1232"), pd.Timestamp("1970-11-30")),
    ]
)
def end_of_month_tests(request):
    """returns the expected input/output of a mysql end_of_month call"""
    return request.param


@pytest.mark.slow
def test_end_of_month(end_of_month_tests):
    assert (
        bodosql.libs.sql_datetime_helpers.mysql_end_of_month(end_of_month_tests[0])
        == end_of_month_tests[1]
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    "input",
    [
        # For mysql timestampdiff, the amount of time that has passed since the begining of
        # the month is compared when determing if a two timestamps differ by a month.
        # for example:
        #   timestampdiff(02-01, 01-01) == 1
        #   timestampdiff(02-01, 01-01 + 1 ns) == 0
        # these test cases check that our helper function replicates this behavior
        # Tests the rounding for day differences
        (pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-31"), 0),
        (pd.Timestamp("2020-02-01"), pd.Timestamp("2020-01-01"), -1),
        (pd.Timestamp("2020-02-02"), pd.Timestamp("2020-01-01"), -1),
        (pd.Timestamp("2022-02-12"), pd.Timestamp("2021-01-12"), -13),
        # tests the rounding on minute/second differences
        (pd.Timestamp("2005-03-01 01:01:00"), pd.Timestamp("2005-02-01 01:01:01"), 0),
        (pd.Timestamp("2005-03-01 01:01:01"), pd.Timestamp("2005-02-01 01:01:01"), -1),
        (
            pd.Timestamp("2006-03-01 01:01:00"),
            pd.Timestamp("2005-02-01 01:01:01"),
            -12,
        ),
        (
            pd.Timestamp("2006-03-13 01:01:00"),
            pd.Timestamp("2005-02-12 01:01:01"),
            -13,
        ),
        (
            pd.Timestamp("2006-03-13 01:01:00"),
            pd.Timestamp("2005-02-13 01:01:01"),
            -12,
        ),
        (
            pd.Timestamp("2006-03-13 01:01:00.0"),
            pd.Timestamp("2005-02-13 01:01:01"),
            -12,
        ),
        (
            pd.Timestamp("2006-03-13 01:02:00.0"),
            pd.Timestamp("2005-02-13 01:01:01"),
            -13,
        ),
        # tests the rounding for fractional time differences
        (
            pd.Timestamp("2005-03-11 11:59:59.99"),
            pd.Timestamp("2005-02-12 01:01:01"),
            0,
        ),
        # tests that day diffs > minute diffs > second diffs... ect.
        (
            pd.Timestamp("2005-03-13 01:01:00.0"),
            pd.Timestamp("2005-02-11 12:59:59.99"),
            -1,
        ),
        (
            pd.Timestamp("2006-03-12 01:01:00.0"),
            pd.Timestamp("2005-02-11 01:10:01.99"),
            -13,
        ),
    ],
)
def test_month_dif(input):
    arg0 = input[0]
    arg1 = input[1]
    expected = input[2]
    assert bodosql.libs.sql_datetime_helpers.mysql_month_diff(arg0, arg1) == expected
    assert bodosql.libs.sql_datetime_helpers.mysql_month_diff(arg1, arg0) == -expected
