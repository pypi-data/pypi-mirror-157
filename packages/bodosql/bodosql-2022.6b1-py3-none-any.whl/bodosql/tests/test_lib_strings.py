# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
Test correctness of bodosql.libs.regex functions
"""

import pytest

import bodosql


@pytest.fixture(
    params=[]
    + [pytest.param((x, chr(x)), marks=pytest.mark.slow) for x in [0, 2, 53, 127]]
    + [pytest.param((ord(s), s), marks=pytest.mark.slow) for s in ["a", "Z", "%", ","]]
)
def chr_ord_tests(request):
    """Tuples of integer values, the corresponding char
    In other words:
    chr(str) == int, && ord(int) = str
    """
    return request.param


@pytest.mark.slow
def test_ord(chr_ord_tests):
    """tests bodosql.libs.string_helpers.bodosql_ord_scalar on the common cases"""
    assert (
        bodosql.libs.string_helpers.bodosql_ord_scalar(chr_ord_tests[1])
        == chr_ord_tests[0]
    )


@pytest.mark.slow
def test_chr(chr_ord_tests):
    """tests bodosql.libs.string_helpers.bodosql_chr_scalar on the common cases"""
    assert (
        bodosql.libs.string_helpers.bodosql_chr_scalar(chr_ord_tests[0])
        == chr_ord_tests[1]
    )


@pytest.mark.slow
@pytest.fixture(
    params=[
        ("hello", ord("h")),
        ("", 0),
    ]
)
def test_ord_edgecases(request):
    """tests bodosql.libs.string_helpers.bodosql_ord_scalar edge cases """
    assert (
        bodosql.libs.string_helpers.bodosql_ord_scalar(request.param[0])
        == request.param[1]
    )


@pytest.mark.slow
@pytest.fixture(
    params=[
        (-1, None),
        (1114111, None),
        (127, "\x7f"),
        (128, None),
        (0, "\x00"),
    ]
)
def test_chr_edgecases(request):
    """tests bodosql.libs.string_helpers.bodosql_chr_scalar edge cases """
    assert (
        bodosql.libs.string_helpers.bodosql_chr_scalar(request.param[0])
        == request.param[1]
    )
