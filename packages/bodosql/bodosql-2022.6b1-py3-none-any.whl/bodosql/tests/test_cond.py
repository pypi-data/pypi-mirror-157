# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
Test correctness of SQL conditional functions on BodoSQL
"""
import numpy as np
import pandas as pd
import pytest
from bodosql.tests.utils import check_query


@pytest.fixture(params=["IFNULL", pytest.param("NVL", marks=pytest.mark.slow)])
def ifnull_equivalent_fn(request):
    return request.param


def test_if_columns(basic_df, spark_info, memory_leak_check):
    """Checks if function with all column values"""
    query = "Select IF(B > C, A, C) from table1"
    check_query(query, basic_df, spark_info, check_names=False, check_dtype=False)


@pytest.mark.slow
def test_if_scalar(basic_df, spark_info, memory_leak_check):
    """Checks if function with all scalar values"""
    query = "Select IF(1 < 2, 7, 31)"
    check_query(query, basic_df, spark_info, check_names=False)


@pytest.mark.slow
def test_if_mixed(basic_df, spark_info, memory_leak_check):
    """Checks if function with a mix of scalar and column values"""
    query = "Select IF(B > C, A, -45) from table1"
    check_query(query, basic_df, spark_info, check_names=False, check_dtype=False)


@pytest.mark.slow
def test_if_case(basic_df, spark_info, memory_leak_check):
    """Checks if function inside a case statement"""
    query = "Select CASE WHEN A > B THEN IF(B > C, A, C) ELSE B END from table1"
    check_query(query, basic_df, spark_info, check_names=False, check_dtype=False)


@pytest.mark.slow
def test_if_null_column(bodosql_nullable_numeric_types, spark_info, memory_leak_check):
    """Checks if function with all nullable columns"""
    query = "Select IF(B > C, A, C) from table1"
    check_query(
        query,
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


@pytest.mark.slow
def test_if_multitable(join_dataframes, spark_info, memory_leak_check):
    """Checks if function with columns from multiple tables"""
    query = "Select IF(table2.B > table1.B, table1.A, table2.A) from table1, table2"
    check_query(
        query, join_dataframes, spark_info, check_names=False, check_dtype=False
    )


def test_ifnull_columns(
    bodosql_nullable_numeric_types, spark_info, ifnull_equivalent_fn, memory_leak_check
):
    """Checks ifnull function with all column values"""

    query = f"Select {ifnull_equivalent_fn}(A, B) from table1"
    spark_query = "Select IFNULL(A, B) from table1"
    check_query(
        query,
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
        equivalent_spark_query=spark_query,
    )


@pytest.mark.slow
def test_ifnull_scalar(basic_df, spark_info, ifnull_equivalent_fn, memory_leak_check):
    """Checks ifnull function with all scalar values"""

    query = f"Select {ifnull_equivalent_fn}(-1, 45)"
    spark_query = "Select IFNULL(-1, 45)"
    check_query(
        query,
        basic_df,
        spark_info,
        check_names=False,
        equivalent_spark_query=spark_query,
    )


@pytest.mark.slow
def test_ifnull_mixed(
    bodosql_nullable_numeric_types, spark_info, ifnull_equivalent_fn, memory_leak_check
):

    if bodosql_nullable_numeric_types["table1"].A.dtype.name == "UInt64":
        pytest.skip("Currently a bug in fillna for Uint64, see BE-1380")

    """Checks ifnull function with a mix of scalar and column values"""
    query = f"Select {ifnull_equivalent_fn}(A, 0) from table1"
    spark_query = "Select IFNULL(A, 0) from table1"
    check_query(
        query,
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
        equivalent_spark_query=spark_query,
    )


@pytest.mark.slow
def test_ifnull_case(
    bodosql_nullable_numeric_types, spark_info, ifnull_equivalent_fn, memory_leak_check
):
    """Checks ifnull function inside a case statement"""
    query = f"Select CASE WHEN A > B THEN {ifnull_equivalent_fn}(A, C) ELSE B END from table1"
    spark_query = "Select CASE WHEN A > B THEN IFNULL(A, C) ELSE B END from table1"
    check_query(
        query,
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
        equivalent_spark_query=spark_query,
    )


@pytest.mark.slow
def test_ifnull_null_float(
    zeros_df, spark_info, ifnull_equivalent_fn, memory_leak_check
):
    """Checks ifnull function with values that generate np.nan"""
    # Note: 1 / 0 returns np.inf in BodoSQL but NULL in Spark, so
    # we use expected Output
    expected_output = pd.DataFrame(
        {"val": (zeros_df["table1"]["A"] / zeros_df["table1"]["B"]).replace(np.nan, -1)}
    )
    query = f"Select {ifnull_equivalent_fn}(A / B, -1) as val from table1"
    check_query(query, zeros_df, spark_info, expected_output=expected_output)


@pytest.mark.slow
def test_ifnull_multitable(
    join_dataframes, spark_info, ifnull_equivalent_fn, memory_leak_check
):
    """Checks ifnull function with columns from multiple tables"""
    if any(
        [
            isinstance(x, pd.core.arrays.integer._IntegerDtype)
            for x in join_dataframes["table1"].dtypes
        ]
    ):
        check_dtype = False
    else:
        check_dtype = True
    query = "Select IFNULL(table2.B, table1.B) from table1, table2"
    spark_query = (
        f"Select {ifnull_equivalent_fn}(table2.B, table1.B) from table1, table2"
    )
    check_query(
        query,
        join_dataframes,
        spark_info,
        check_names=False,
        equivalent_spark_query=spark_query,
        check_dtype=check_dtype,
    )


def test_nullif_columns(bodosql_nullable_numeric_types, spark_info, memory_leak_check):
    """Checks nullif function with all column values"""
    query = "Select NULLIF(MOD(A, 2), MOD(B, 2)) from table1"
    check_query(
        query,
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
        convert_float_nan=True,
    )


@pytest.mark.skip("Support setting a NULL scalar")
def test_nullif_scalar(basic_df, spark_info, memory_leak_check):
    """Checks nullif function with all scalar values"""
    query = "Select NULLIF(0, 0) from table1"
    check_query(query, basic_df, spark_info, check_names=False)


@pytest.mark.slow
def test_nullif_mixed(bodosql_nullable_numeric_types, spark_info, memory_leak_check):
    """Checks nullif function with a mix of scalar and column values"""
    query = "Select NULLIF(MOD(A, 2), 1) from table1"
    check_query(
        query,
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
        convert_float_nan=True,
    )


@pytest.mark.slow
def test_nullif_case(bodosql_nullable_numeric_types, spark_info, memory_leak_check):
    """Checks nullif function inside a case statement"""
    query = "Select CASE WHEN A > B THEN NULLIF(A, C) ELSE B END from table1"
    check_query(
        query,
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


@pytest.mark.slow
def test_nullif_multitable(join_dataframes, spark_info, memory_leak_check):
    """Checks nullif function with columns from multiple tables"""
    if any(
        [
            isinstance(x, pd.core.arrays.integer._IntegerDtype)
            for x in join_dataframes["table1"].dtypes
        ]
    ):
        check_dtype = False
    else:
        check_dtype = True
    query = "Select NULLIF(table2.B, table1.B) from table1, table2"
    check_query(
        query, join_dataframes, spark_info, check_names=False, check_dtype=check_dtype
    )
