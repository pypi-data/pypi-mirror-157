# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
Test correctness of SQL aggregation operations with groupby on BodoSQL
"""
import numpy as np
import pandas as pd
import pytest

from bodosql.tests.utils import check_query


@pytest.fixture
def grouped_dfs():
    """
    A dataFrame larger amounts of data per group.
    This ensures we get meaningful results with
    groupby functions.
    """
    return {
        "table1": pd.DataFrame(
            {
                "A": [0, 1, 2, 4] * 50,
                "B": np.arange(200),
                "C": [1.5, 2.24, 3.52, 4.521, 5.2353252, -7.3, 23, -0.341341] * 25,
            }
        )
    }


@pytest.mark.slow
def test_agg_numeric(
    bodosql_numeric_types, numeric_agg_builtin_funcs, spark_info, memory_leak_check
):
    """test aggregation calls in queries"""
    # Skipping VAR_POP and STDDEV_POP with groupby due to [BE-910]
    if (
        numeric_agg_builtin_funcs == "STDDEV_POP"
        or numeric_agg_builtin_funcs == "VAR_POP"
    ):
        return

    # bitwise aggregate function only valid on integers
    if numeric_agg_builtin_funcs in {"BIT_XOR", "BIT_OR", "BIT_AND"}:
        if not np.issubdtype(bodosql_numeric_types["table1"]["A"].dtype, np.integer):
            return

    query = f"select {numeric_agg_builtin_funcs}(B), {numeric_agg_builtin_funcs}(C) from table1 group by A"

    check_query(
        query, bodosql_numeric_types, spark_info, check_dtype=False, check_names=False
    )


def test_agg_numeric_larger_group(
    grouped_dfs, numeric_agg_builtin_funcs, spark_info, memory_leak_check
):
    """test aggregation calls in queries on DataFrames with a larger data in each group."""
    # Skipping VAR_POP and STDDEV_POP with groupby due to [BE-910]
    if (
        numeric_agg_builtin_funcs == "STDDEV_POP"
        or numeric_agg_builtin_funcs == "VAR_POP"
    ):
        return

    # bitwise aggregate function only valid on integers
    if numeric_agg_builtin_funcs in {"BIT_XOR", "BIT_OR", "BIT_AND"}:
        if not np.issubdtype(bodosql_numeric_types["table1"]["A"].dtype, np.integer):
            return

    query = f"select {numeric_agg_builtin_funcs}(B), {numeric_agg_builtin_funcs}(C) from table1 group by A"

    check_query(query, grouped_dfs, spark_info, check_dtype=False, check_names=False)


@pytest.mark.slow
def test_aliasing_agg_numeric(
    bodosql_numeric_types, numeric_agg_builtin_funcs, spark_info, memory_leak_check
):
    """test aliasing of aggregations in queries"""
    # Skipping VAR_POP and STDDEV_POP with groupby due to [BE-910]
    if (
        numeric_agg_builtin_funcs == "STDDEV_POP"
        or numeric_agg_builtin_funcs == "VAR_POP"
    ):
        return

    # bitwise aggregate function only valid on integers
    if numeric_agg_builtin_funcs in {"BIT_XOR", "BIT_OR", "BIT_AND"}:
        if not np.issubdtype(bodosql_numeric_types["table1"]["A"].dtype, np.integer):
            return

    query = f"select {numeric_agg_builtin_funcs}(B) as testCol from table1 group by A"

    check_query(
        query, bodosql_numeric_types, spark_info, check_dtype=False, check_names=False
    )


def test_count_numeric(bodosql_numeric_types, spark_info, memory_leak_check):
    """test various count queries on numeric data."""
    check_query(
        "SELECT COUNT(Distinct B) FROM table1 group by A",
        bodosql_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) FROM table1 group by A",
        bodosql_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


def test_count_nullable_numeric(
    bodosql_nullable_numeric_types, spark_info, memory_leak_check
):
    """test various count queries on nullable numeric data."""
    check_query(
        "SELECT COUNT(Distinct B) FROM table1 group by A",
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) FROM table1 group by A",
        bodosql_nullable_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


def test_count_datetime(bodosql_datetime_types, spark_info, memory_leak_check):
    """test various count queries on Timestamp data."""
    check_query(
        "SELECT COUNT(Distinct B) FROM table1 group by A",
        bodosql_datetime_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) FROM table1 group by A",
        bodosql_datetime_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


def test_count_interval(bodosql_interval_types, spark_info, memory_leak_check):
    """test various count queries on Timedelta data."""
    check_query(
        "SELECT COUNT(Distinct B) FROM table1 group by A",
        bodosql_interval_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) FROM table1 group by A",
        bodosql_interval_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


def test_count_string(bodosql_string_types, spark_info, memory_leak_check):
    """test various count queries on string data."""
    check_query(
        "SELECT COUNT(Distinct B) FROM table1 group by A",
        bodosql_string_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) FROM table1 group by A",
        bodosql_string_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


@pytest.mark.skip("[BE-958] Support for equality with Binary data.")
def test_count_binary(bodosql_binary_types, spark_info, memory_leak_check):
    """test various count queries on binary data."""
    check_query(
        "SELECT COUNT(Distinct B) FROM table1 group by A",
        bodosql_binary_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) FROM table1 group by A",
        bodosql_binary_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


def test_count_boolean(bodosql_boolean_types, spark_info, memory_leak_check):
    """test various count queries on boolean data."""
    check_query(
        "SELECT COUNT(Distinct B) FROM table1 group by A",
        bodosql_boolean_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) FROM table1 group by A",
        bodosql_boolean_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


@pytest.mark.slow
def test_count_numeric_alias(bodosql_numeric_types, spark_info, memory_leak_check):
    """test various count queries on numeric data with aliases."""
    check_query(
        "SELECT COUNT(Distinct B) as alias FROM table1 group by A",
        bodosql_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )
    check_query(
        "SELECT COUNT(*) as alias FROM table1 group by A",
        bodosql_numeric_types,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


@pytest.mark.slow
def test_having_repeat_numeric(bodosql_numeric_types, spark_info, memory_leak_check):
    """test having clause in numeric queries"""
    check_query(
        "select sum(B) from table1 group by a having count(b) >1",
        bodosql_numeric_types,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


def test_having_repeat_datetime(bodosql_datetime_types, spark_info, memory_leak_check):
    """test having clause in datetime queries"""
    check_query(
        f"select count(B) from table1 group by a having count(b) > 2",
        bodosql_datetime_types,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


def test_having_repeat_interval(bodosql_interval_types, spark_info, memory_leak_check):
    """test having clause in datetime queries"""
    check_query(
        f"select count(B) from table1 group by a having count(b) > 2",
        bodosql_interval_types,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


@pytest.mark.slow
def test_agg_repeat_col(bodosql_numeric_types, spark_info, memory_leak_check):
    """test aggregations repeating the same column"""
    check_query(
        "select max(A), min(A), avg(A) from table1 group by B",
        bodosql_numeric_types,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


@pytest.mark.slow
def test_groupby_bool(bodosql_boolean_types, spark_info, memory_leak_check):
    """
    Simple test to ensure that groupby and max are working on boolean types
    """
    query = """
        SELECT
            max(B)
        FROM
            table1
        GROUP BY
            A
        """
    check_query(
        query, bodosql_boolean_types, spark_info, check_names=False, check_dtype=False
    )


def test_groupby_string(bodosql_string_types, spark_info, memory_leak_check):
    """
    Simple test to ensure that groupby and max are working on string types
    """
    query = """
        SELECT
            max(B)
        FROM
            table1
        GROUP BY
            A
        """
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


@pytest.mark.slow
def test_groupby_numeric_scalars(basic_df, spark_info, memory_leak_check):
    """
    tests to ensure that groupby and max are working with numeric scalars
    """
    query = """
        SELECT
            max(B), 1 as E, 2 as F
        FROM
            table1
        GROUP BY
            A
        """
    check_query(query, basic_df, spark_info, check_names=False)


def test_groupby_datetime_types(bodosql_datetime_types, spark_info, memory_leak_check):
    """
    Simple test to ensure that groupby and max are working on datetime types
    """
    query = """
        SELECT
            max(B)
        FROM
            table1
        GROUP BY
            A
        """
    check_query(
        query,
        bodosql_datetime_types,
        spark_info,
        check_names=False,
    )


def test_groupby_interval_types(bodosql_interval_types, spark_info, memory_leak_check):
    """
    Simple test to ensure that groupby and max are working on interval types
    """
    query = """
        SELECT
            max(B) as output
        FROM
            table1
        GROUP BY
            A
        """
    check_query(
        query,
        bodosql_interval_types,
        spark_info,
        convert_columns_timedelta=["output"],
    )


def test_having_numeric(
    bodosql_numeric_types,
    comparison_ops,
    spark_info,
    # seems to be leaking memory sporatically, see [BS-534]
    # memory_leak_check
):
    """
    Tests having with a constant and groupby.
    """
    query = f"""
        SELECT
           MAX(A)
        FROM
            table1
        Group By
            C
        HAVING
            max(B) {comparison_ops} 1
        """
    check_query(
        query,
        bodosql_numeric_types,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


def test_having_boolean_agg_cond(bodosql_boolean_types, spark_info, memory_leak_check):
    """
    Tests groupby + having with aggregation in the condition
    """
    query = f"""
        SELECT
           MAX(A)
        FROM
            table1
        GROUP BY
            C
        HAVING
            max(B) <> True
        """
    check_query(
        query,
        bodosql_boolean_types,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


def test_having_boolean_groupby_cond(
    bodosql_boolean_types, spark_info, memory_leak_check
):
    """
    Tests groupby + having using the groupby column in the having condtion
    """
    query = f"""
        SELECT
           MAX(A)
        FROM
            table1
        GROUP BY
            C
        HAVING
            C <> True
        """
    check_query(
        query,
        bodosql_boolean_types,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


@pytest.mark.slow
def test_repeat_columns(basic_df, spark_info, memory_leak_check):
    """
    Tests that a column that won't produce a conflicting name
    even if it performs the same operation.
    """
    query = "Select sum(A), sum(A) as alias from table1 group by B"
    check_query(
        query,
        basic_df,
        spark_info,
        check_dtype=False,
        check_names=False,
    )


@pytest.mark.slow
def test_no_rename(basic_df, spark_info, memory_leak_check):
    """
    Tests that a columns with legal Python identifiers aren't renamed
    in simple queries (no intermediate names).
    """
    query = "Select sum(A) as col1, max(A) as col2 from table1 group by B"
    result = check_query(
        query, basic_df, spark_info, check_dtype=False, return_codegen=True
    )
    pandas_code = result["pandas_code"]
    assert "rename" not in pandas_code


@pytest.mark.slow
def test_rename(basic_df, spark_info, memory_leak_check):
    """
    Tests that a columns without a legal Python identifiers is renamed
    in a simple query (no intermediate names).
    """
    query = "Select sum(A) as `sum(A)`, max(A) as `max(A)` from table1 group by B"
    result = check_query(
        query, basic_df, spark_info, check_dtype=False, return_codegen=True
    )
    pandas_code = result["pandas_code"]
    assert "rename" in pandas_code
