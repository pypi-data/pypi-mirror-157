# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
Test correctness of SQL coalesce funcion in BodoSQL
"""
import pandas as pd
import pytest
from bodosql.tests.utils import check_query


def test_coalesce_cols(spark_info, basic_df, memory_leak_check):
    """tests the coalesce function on column values"""
    query = "select COALESCE(A, B, C) from table1"

    check_query(query, basic_df, spark_info, check_dtype=False, check_names=False)


@pytest.mark.slow
def test_coalesce_scalars(spark_info, basic_df, memory_leak_check):
    """tests the coalesce function on scalar values"""
    query = "select CASE WHEN COALESCE(A, B, C) = B THEN -1 ELSE COALESCE(A, B, C) END from table1"

    check_query(query, basic_df, spark_info, check_dtype=False, check_names=False)


@pytest.mark.skip(
    "We're currently treating the behavior of coalesce on variable types as undefined behavior, see BS-435"
)
def test_coalesce_variable_type_cols(
    spark_info,
    bodosql_datetime_types,
    bodosql_string_types,
    basic_df,
    memory_leak_check,
):
    """tests the coalesce function on column values which have varying types

    Currently, Calcite allows for variable types in coalesce, so long as they converge to
    some common type. For our purposes this behavior is undefined.
    """
    new_ctx = {
        "table1": pd.DataFrame(
            {
                "A": bodosql_datetime_types["table1"]["A"],
                "B": bodosql_string_types["table1"]["B"],
                "C": basic_df["table1"]["C"],
            }
        )
    }
    query = "select COALESCE(A, B, C) from table1"

    check_query(query, new_ctx, spark_info, check_dtype=False, check_names=False)


@pytest.mark.skip(
    "We're currently treating the behavior of coalesce on variable types as undefined behavior, see BS-435"
)
def test_coalesce_variable_type_scalars(
    spark_info,
    bodosql_datetime_types,
    bodosql_string_types,
    basic_df,
    memory_leak_check,
):
    """tests the coalesce function on scalar values which have varying types

    Currently, Calcite allows for variable types in coalesce, so long as they converge to
    some common type. For our purposes this behavior is undefined.
    """
    new_ctx = {
        "table1": pd.DataFrame(
            {
                "A": bodosql_datetime_types["table1"]["A"],
                "B": bodosql_string_types["table1"]["B"],
                "C": basic_df["table1"]["C"],
            }
        )
    }
    query = "select CASE WHEN COALESCE(A, B, C) = B THEN C ELSE COALESCE(A, B, C) END from table1"

    check_query(query, new_ctx, spark_info, check_dtype=False, check_names=False)
