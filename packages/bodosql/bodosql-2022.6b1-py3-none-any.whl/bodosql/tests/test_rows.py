"""
Tests the behavior of windowed agregations functions with the OVER clause

Currently, all tests in this file only check the 1D Var case. This is to avoid
excessive memory leak, see [BS-530/BE-947]
"""

import numpy as np
import pandas as pd
import pytest

from bodosql.tests.utils import bodo_version_older, check_query

# Helper global value to allow for testing locally, while avoiding
# memory issues on CI
testing_locally = False


@pytest.fixture(
    params=[
        pytest.param(
            ("CURRENT ROW", "UNBOUNDED FOLLOWING"),
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        ("UNBOUNDED PRECEDING", "1 PRECEDING"),
        pytest.param(
            ("1 PRECEDING", "1 FOLLOWING"),
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        pytest.param(
            ("CURRENT ROW", "1 FOLLOWING"),
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        pytest.param(
            ("CURRENT ROW", "CURRENT ROW"),
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        pytest.param(
            ("1 FOLLOWING", "2 FOLLOWING"),
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        pytest.param(
            ("UNBOUNDED PRECEDING", "2 FOLLOWING"),
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        pytest.param(
            ("3 PRECEDING", "UNBOUNDED FOLLOWING"),
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
    ]
)
def over_clause_bounds(request):
    """fixture containing the upper/lower bounds for the SQL OVER clause"""
    return request.param


@pytest.fixture(params=["LEAD", "LAG"])
def lead_or_lag(request):
    return request.param


@pytest.fixture(
    params=[
        "MAX",
        pytest.param(
            "MIN",
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        pytest.param("COUNT", marks=pytest.mark.slow),
        "COUNT(*)",
        pytest.param("SUM", marks=pytest.mark.slow),
        "AVG",
        "STDDEV",
        pytest.param(
            "STDDEV_POP",
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        pytest.param("VARIANCE", marks=pytest.mark.slow),
        pytest.param(
            "VAR_POP",
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        "FIRST_VALUE",
        "LAST_VALUE",
    ]
)
def numeric_agg_funcs_subset(request):
    """subset of numeric agregation functions, used for testing windowed behavior"""
    return request.param


@pytest.fixture(
    params=[
        "MAX",
        pytest.param(
            "MIN",
            marks=pytest.mark.skipif(
                not testing_locally, reason="Fix Memory Leak error"
            ),
        ),
        "COUNT",
        "COUNT(*)",
        "FIRST_VALUE",
        "LAST_VALUE",
    ]
)
def non_numeric_agg_funcs_subset(request):
    """subset of non_numeric aggregation functions, used for testing windowed behavior"""
    return request.param


# TODO: fix memory leak issues with groupby apply, see [BS-530/BE-947]
def test_windowed_upper_lower_bound_numeric(
    bodosql_numeric_types,
    numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    # memory_leak_check,
):
    """Tests windowed agregations works when both bounds are specified"""

    # remove once memory leak is resolved
    df_dtype = bodosql_numeric_types["table1"]["A"].dtype
    if not (
        testing_locally
        or np.issubdtype(df_dtype, np.float64)
        or np.issubdtype(df_dtype, np.int64)
    ):
        pytest.skip("Skipped due to memory leak")

    if numeric_agg_funcs_subset == "COUNT(*)":
        agg_fn_call = "COUNT(*)"
    else:
        agg_fn_call = f"{numeric_agg_funcs_subset}(A)"

    window_ASC = f"(PARTITION BY B ORDER BY C ASC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    window_DESC = f"(PARTITION BY B ORDER BY C DESC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"

    # doing an orderby in the query so it's easier to tell what the error is by visual comparison
    # should an error occur
    query = f"select A, B, C, {agg_fn_call} OVER {window_ASC} as WINDOW_AGG_ASC, {agg_fn_call} OVER {window_DESC} as WINDOW_AGG_DESC FROM table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_numeric_types,
        spark_info,
        sort_output=False,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


# TODO: fix memory leak issues with groupby apply, see [BS-530/BE-947]
def test_windowed_upper_lower_bound_numeric_inside_case(
    bodosql_numeric_types,
    numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    # memory_leak_check,
):
    """Tests windowed agregations works when both bounds are specified"""

    # remove once memory leak is resolved
    df_dtype = bodosql_numeric_types["table1"]["A"].dtype
    if not (
        testing_locally
        or np.issubdtype(df_dtype, np.float64)
        or np.issubdtype(df_dtype, np.int64)
    ):
        pytest.skip("Skipped due to memory leak")

    if numeric_agg_funcs_subset == "COUNT(*)":
        agg_fn_call = "COUNT(*)"
    else:
        agg_fn_call = f"{numeric_agg_funcs_subset}(A)"

    window = f"(PARTITION BY B ORDER BY C ASC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"

    # doing an orderby in the query so it's easier to tell what the error is by visual comparison
    # should an error occur
    query = f"select A, B, C, CASE WHEN {agg_fn_call} OVER {window} > 0 THEN {agg_fn_call} OVER {window} ELSE -({agg_fn_call} OVER {window}) END FROM table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_numeric_types,
        spark_info,
        sort_output=False,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


# TODO: fix memory leak issues with groupby apply, see [BS-530/BE-947]
@pytest.mark.slow
def test_windowed_upper_lower_bound_timestamp(
    bodosql_datetime_types,
    non_numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    # memory_leak_check,
):
    """Tests windowed agregations works when both bounds are specified on timestamp types"""

    if non_numeric_agg_funcs_subset == "COUNT(*)":
        agg_fn_call = "COUNT(*)"
    else:
        agg_fn_call = f"{non_numeric_agg_funcs_subset}(A)"

    # Switched partition/sortby to avoid null
    window_ASC = f"(PARTITION BY C ORDER BY A ASC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    window_DESC = f"(PARTITION BY C ORDER BY A DESC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"

    # doing an orderby in the query so it's easier to tell what the error is by visual comparison
    # should an error occur.
    query = f"select A, C, {agg_fn_call} OVER {window_ASC} as WINDOW_AGG_ASC, {agg_fn_call} OVER {window_DESC} as WINDOW_AGG_DESC FROM table1 ORDER BY C, A"

    check_query(
        query,
        bodosql_datetime_types,
        spark_info,
        sort_output=False,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_windowed_upper_lower_bound_string(
    bodosql_string_types,
    non_numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    # memory_leak_check,
):
    """Tests windowed agregations works when both bounds are specified on string types"""

    if non_numeric_agg_funcs_subset in ["MAX", "MIN"]:
        pytest.skip()
    if non_numeric_agg_funcs_subset == "COUNT(*)":
        agg_fn_call = "COUNT(*)"
    else:
        agg_fn_call = f"{non_numeric_agg_funcs_subset}(A)"

    # Switched partition/sortby to avoid null
    window_ASC = f"(PARTITION BY C ORDER BY A ASC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    window_DESC = f"(PARTITION BY C ORDER BY A DESC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"

    # doing an orderby in the query so it's easier to tell what the error is by visual comparison
    # should an error occur.
    query = f"select A, C, {agg_fn_call} OVER {window_ASC} as WINDOW_AGG_ASC, {agg_fn_call} OVER {window_DESC} as WINDOW_AGG_DESC FROM table1 ORDER BY C, A"

    check_query(
        query,
        bodosql_string_types,
        spark_info,
        sort_output=False,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_windowed_upper_lower_bound_binary(
    bodosql_binary_types,
    non_numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    # memory_leak_check,
):
    """Tests windowed agregations works when both bounds are specified on binary types"""
    """NOTE: this function currently doesn't run, as the binary types fixture is disabled"""

    if non_numeric_agg_funcs_subset in ["MAX", "MIN"]:
        pytest.skip()
    if non_numeric_agg_funcs_subset == "COUNT(*)":
        agg_fn_call = "COUNT(*)"
    else:
        agg_fn_call = f"{non_numeric_agg_funcs_subset}(A)"

    # Switched partition/sortby to avoid null
    window_ASC = f"(PARTITION BY C ORDER BY A ASC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    window_DESC = f"(PARTITION BY C ORDER BY A DESC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"

    # doing an orderby in the query so it's easier to tell what the error is by visual comparison
    # should an error occur.
    query = f"select A, C, {agg_fn_call} OVER {window_ASC} as WINDOW_AGG_ASC, {agg_fn_call} OVER {window_DESC} as WINDOW_AGG_DESC FROM table1 ORDER BY C, A"

    check_query(
        query,
        bodosql_binary_types,
        spark_info,
        sort_output=False,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_windowed_upper_lower_bound_timedelta(
    bodosql_interval_types, non_numeric_agg_funcs_subset, over_clause_bounds, spark_info
):
    """Tests windowed agregations works when both bounds are specified on timedelta types"""

    if non_numeric_agg_funcs_subset == "COUNT(*)":
        agg_fn_call = "COUNT(*)"
    else:
        agg_fn_call = f"{non_numeric_agg_funcs_subset}(A)"

    # Switched partition/sortby to avoid null
    window_ASC = f"(PARTITION BY C ORDER BY A ASC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    window_DESC = f"(PARTITION BY C ORDER BY A ASC ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"

    # doing an orderby in the query so it's easier to tell what the error is by visual comparison
    # should an error occur
    query = f"select A as A, C as C, {agg_fn_call} OVER {window_ASC} as WINDOW_AGG_ASC, {agg_fn_call} OVER {window_DESC} as WINDOW_AGG_DESC FROM table1 ORDER BY C, A"

    if (
        non_numeric_agg_funcs_subset == "COUNT"
        or non_numeric_agg_funcs_subset == "COUNT(*)"
    ):
        check_query(
            query,
            bodosql_interval_types,
            spark_info,
            sort_output=False,
            check_dtype=False,
            check_names=False,
            convert_columns_timedelta=["A", "C"],
            only_jit_1DVar=True,
        )
    else:
        # need to do a conversion, since spark timedeltas are converted to int64's
        check_query(
            query,
            bodosql_interval_types,
            spark_info,
            sort_output=False,
            check_dtype=False,
            check_names=False,
            convert_columns_timedelta=["A", "C", "WINDOW_AGG_ASC", "WINDOW_AGG_DESC"],
            only_jit_1DVar=True,
        )


@pytest.mark.skip("Defaults to Unbounded window in some case, TODO")
def test_windowed_only_upper_bound(
    basic_df,
    numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    memory_leak_check,
):
    """Tests windowed agregations works when only the upper bound is specified"""

    if over_clause_bounds[0] == "1 FOLLOWING":
        # It seems like Calcite will rearange the window bounds to make sense, but mysql/spark don't?
        # However, we only see this issue for n = 3?
        pytest.skip("Skipped due to memory leak")

    # doing an orderby in the query so it's easier to tell what the error is by visual comparison
    # should an error occur
    query = f"select A, B, C, {numeric_agg_funcs_subset}(A) OVER (PARTITION BY B ORDER BY C ASC ROWS {over_clause_bounds[0]}) as WINDOW_AGG_ASC, {numeric_agg_funcs_subset}(A) OVER (PARTITION BY B ORDER BY C DESC ROWS {over_clause_bounds[0]} ) as WINDOW_AGG_DESC FROM table1 ORDER BY B, C"

    # spark windowed min/max on integers returns an integer col.
    # pandas rolling min/max on integer series returns a float col
    # (and the method that we currently use returns a float col)
    cols_to_cast = [("WINDOW_AGG_ASC", "float64"), ("WINDOW_AGG_DESC", "float64")]

    check_query(
        query,
        basic_df,
        spark_info,
        check_dtype=False,
        check_names=False,
        spark_output_cols_to_cast=cols_to_cast,
        only_jit_1DVar=True,
    )


@pytest.mark.skip("TODO")
def test_empty_window(
    basic_df,
    numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    memory_leak_check,
):
    """Tests windowed agregations works when no bounds are specified"""
    query = f"select A, B, C, {numeric_agg_funcs_subset}(A) OVER () as WINDOW_AGG FROM table1"

    # spark windowed min/max on integers returns an integer col.
    # pandas rolling min/max on integer series returns a float col
    # (and the method that we currently use returns a float col)
    cols_to_cast = [("WINDOW_AGG", "float64")]

    check_query(
        query,
        basic_df,
        spark_info,
        check_dtype=False,
        check_names=False,
        spark_output_cols_to_cast=cols_to_cast,
        only_jit_1DVar=True,
    )


@pytest.mark.skip("TODO")
def test_nested_windowed_agg(
    basic_df,
    numeric_agg_funcs_subset,
    over_clause_bounds,
    spark_info,
    memory_leak_check,
):
    """Tests windowed agregations works when performing agregations, sorting by, and bounding by non constant values"""

    # doing an orderby and calculating extra rows in the query so it's easier to tell what the error is by visual comparison
    query = f"SELECT A, B, C, {numeric_agg_funcs_subset}(B) OVER (PARTITION BY A ORDER BY C ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) as WINDOW_AGG, CASE WHEN A > 1 THEN A * {numeric_agg_funcs_subset}(B) OVER (PARTITION BY A ORDER BY C ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]}) ELSE -1 END AS NESTED_WINDOW_AGG from table1 ORDER BY A, C"

    # spark windowed min/max on integers returns an integer col.
    # pandas rolling min/max on integer series returns a float col
    # (and the method that we currently use returns a float col)
    cols_to_cast = [("WINDOW_AGG", "float64"), ("NESTED_WINDOW_AGG", "float64")]
    check_query(
        query,
        basic_df,
        spark_info,
        sort_output=False,
        check_dtype=False,
        check_names=False,
        spark_output_cols_to_cast=cols_to_cast,
        only_jit_1DVar=True,
    )


def test_lead_lag_consts(
    bodosql_numeric_types,
    lead_or_lag,
    spark_info,
    # memory_leak_check
):
    """tests the lead and lag agregation functions"""

    # remove once memory leak is resolved
    df_dtype = bodosql_numeric_types["table1"]["A"].dtype
    if not (
        testing_locally
        or np.issubdtype(df_dtype, np.float64)
        or np.issubdtype(df_dtype, np.int64)
    ):
        pytest.skip("Skipped due to memory leak")

    window = "(PARTITION BY B ORDER BY C)"
    lead_lag_queries = ", ".join(
        [
            f"{lead_or_lag}(A, {x}) OVER {window} as {lead_or_lag}_{name}"
            for x, name in [(0, "0"), (1, "1"), (-1, "negative_1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {lead_lag_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_numeric_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_lead_lag_consts_datetime(bodosql_datetime_types, lead_or_lag, spark_info):
    """tests the lead and lag agregation functions on datetime types"""

    window = "(PARTITION BY B ORDER BY C)"
    lead_lag_queries = ", ".join(
        [
            f"{lead_or_lag}(A, {x}) OVER {window} as {lead_or_lag}_{name}"
            for x, name in [(0, "0"), (1, "1"), (-1, "negative_1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {lead_lag_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_datetime_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_lead_lag_consts_string(bodosql_string_types, lead_or_lag, spark_info):
    """tests the lead and lag agregation functions on datetime types"""

    window = "(PARTITION BY B ORDER BY C)"
    lead_lag_queries = ", ".join(
        [
            f"{lead_or_lag}(A, {x}) OVER {window} as {lead_or_lag}_{name}"
            for x, name in [(0, "0"), (1, "1"), (-1, "negative_1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {lead_lag_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_lead_lag_consts_binary(bodosql_binary_types, lead_or_lag, spark_info):
    """tests the lead and lag agregation functions on datetime types"""
    """NOTE: this function currently doesn't run, as the binary types fixture is disabled"""

    window = "(PARTITION BY B ORDER BY C)"
    lead_lag_queries = ", ".join(
        [
            f"{lead_or_lag}(A, {x}) OVER {window} as {lead_or_lag}_{name}"
            for x, name in [(0, "0"), (1, "1"), (-1, "negative_1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {lead_lag_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_binary_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
@pytest.mark.skipif(
    bodo_version_older(2021, 8, 1),
    reason="Requires engine changes to support series.shift on timedelta64[ns]",
)
def test_lead_lag_consts_timedelta(bodosql_interval_types, lead_or_lag, spark_info):
    """tests the lead and lag agregation functions on timedelta types"""

    window = "(PARTITION BY B ORDER BY C)"
    lead_lag_queries = ", ".join(
        [
            f"{lead_or_lag}(A, {x}) OVER {window} as {lead_or_lag}_{name}"
            for x, name in [(0, "0"), (1, "1"), (-1, "negative_1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {lead_lag_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_interval_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        convert_columns_timedelta=[
            "A",
            "B",
            "C",
            f"{lead_or_lag}_0",
            f"{lead_or_lag}_1",
            f"{lead_or_lag}_negative_1",
            f"{lead_or_lag}_3",
        ],
        only_jit_1DVar=True,
    )


def test_row_number_numeric(
    bodosql_numeric_types,
    spark_info,
    # memory_leak_check
):
    """tests the row number agregation function on numeric types"""

    # remove once memory leak is resolved
    df_dtype = bodosql_numeric_types["table1"]["A"].dtype
    if not (
        testing_locally
        or np.issubdtype(df_dtype, np.float64)
        or np.issubdtype(df_dtype, np.int64)
    ):
        pytest.skip("Skipped due to memory leak")

    query = f"select A, B, C, ROW_NUMBER() OVER (PARTITION BY B ORDER BY C) from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_numeric_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_row_number_datetime(bodosql_datetime_types, spark_info):
    """tests the row number agregation function on datetime types"""

    query = f"select A, B, C, ROW_NUMBER() OVER (PARTITION BY B ORDER BY C) from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_datetime_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_row_number_timedelta(bodosql_interval_types, spark_info):
    """tests the row_number agregation functions on timedelta types"""

    query = f"select A, B, C, ROW_NUMBER() OVER (PARTITION BY B ORDER BY C) as ROW_NUM from table1 ORDER BY B, C"
    check_query(
        query,
        bodosql_interval_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        convert_columns_timedelta=[
            "A",
            "B",
            "C",
        ],
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_row_number_string(bodosql_string_types, spark_info):
    """tests the row_number agregation functions on timedelta types"""

    query = f"select A, B, C, ROW_NUMBER() OVER (PARTITION BY B ORDER BY C) as ROW_NUM from table1 ORDER BY B, C"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_row_number_binary(bodosql_binary_types, spark_info):
    """tests the row_number agregation functions on timedelta types"""
    """NOTE: doesn't currently run, as bodosql_binary_types fixture is skipped"""

    query = f"select A, B, C, ROW_NUMBER() OVER (PARTITION BY B ORDER BY C) as ROW_NUM from table1 ORDER BY B, C"
    check_query(
        query,
        bodosql_binary_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


def test_nth_value_numeric(bodosql_numeric_types, over_clause_bounds, spark_info):
    """tests the Nth value agregation functon on numeric types"""

    # remove once memory leak is resolved
    df_dtype = bodosql_numeric_types["table1"]["A"].dtype
    if not (
        testing_locally
        or np.issubdtype(df_dtype, np.float64)
        or np.issubdtype(df_dtype, np.int64)
    ):
        pytest.skip("Skipped due to memory leak")

    window = f"(PARTITION BY B ORDER BY C ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    nth_val_queries = ", ".join(
        [
            f"NTH_VALUE(A, {x}) OVER {window} as NTH_VALUE_{name}"
            for x, name in [(1, "1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {nth_val_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_numeric_types,
        spark_info,
        check_dtype=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_nth_value_datetime(bodosql_datetime_types, over_clause_bounds, spark_info):
    """tests the Nth value agregation functon on numeric types"""

    window = f"(PARTITION BY B ORDER BY C ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    nth_val_queries = ", ".join(
        [
            f"NTH_VALUE(A, {x}) OVER {window} as NTH_VALUE_{name}"
            for x, name in [(1, "1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {nth_val_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_datetime_types,
        spark_info,
        check_dtype=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_nth_value_timedelta(bodosql_interval_types, over_clause_bounds, spark_info):
    """tests the Nth value agregation functon on numeric types"""

    window = f"(PARTITION BY B ORDER BY C ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    nth_val_queries = ", ".join(
        [
            f"NTH_VALUE(A, {x}) OVER {window} as NTH_VALUE_{name}"
            for x, name in [(1, "1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {nth_val_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_interval_types,
        spark_info,
        check_dtype=False,
        only_jit_1DVar=True,
        convert_columns_timedelta=["A", "B", "C", "NTH_VALUE_1", "NTH_VALUE_3"],
    )


@pytest.mark.slow
def test_nth_value_string(bodosql_string_types, over_clause_bounds, spark_info):
    """tests the Nth value agregation functon on numeric types"""

    window = f"(PARTITION BY B ORDER BY C ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    nth_val_queries = ", ".join(
        [
            f"NTH_VALUE(A, {x}) OVER {window} as NTH_VALUE_{name}"
            for x, name in [(1, "1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {nth_val_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_dtype=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_nth_value_binary(bodosql_binary_types, over_clause_bounds, spark_info):
    """tests the Nth value agregation functon on numeric types"""
    """NOTE: doesn't currently run, as bodosql_binary_types fixture is skipped"""

    window = f"(PARTITION BY B ORDER BY C ROWS BETWEEN {over_clause_bounds[0]} AND {over_clause_bounds[1]})"
    nth_val_queries = ", ".join(
        [
            f"NTH_VALUE(A, {x}) OVER {window} as NTH_VALUE_{name}"
            for x, name in [(1, "1"), (3, "3")]
        ]
    )
    query = f"select A, B, C, {nth_val_queries} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_binary_types,
        spark_info,
        check_dtype=False,
        only_jit_1DVar=True,
    )


def test_ntile_numeric(
    bodosql_numeric_types,
    spark_info,
    # TODO: re-add memory leak check once the root cause is identified/fixed
    # memory_leak_check
):
    """tests the ntile agregation function with numeric data"""

    # remove once memory leak is resolved
    df_dtype = bodosql_numeric_types["table1"]["A"].dtype
    if not (
        testing_locally
        or np.issubdtype(df_dtype, np.float64)
        or np.issubdtype(df_dtype, np.int64)
    ):
        pytest.skip("Skipped due to memory leak")

    fns = ", ".join(
        f"NTILE({x}) OVER (PARTITION BY B ORDER BY C) as NTILE_{x}" for x in [1, 3, 100]
    )

    query = f"select A, B, C, {fns} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_numeric_types,
        spark_info,
        check_dtype=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_ntile_datetime(bodosql_datetime_types, spark_info):
    """tests the ntile agregation function with datetime data"""

    fns = ", ".join(
        f"NTILE({x}) OVER (PARTITION BY B ORDER BY C) as NTILE_{x}" for x in [1, 3, 100]
    )

    query = f"select A, B, C, {fns} from table1 ORDER BY B, C"

    check_query(
        query,
        bodosql_datetime_types,
        spark_info,
        check_dtype=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_ntile_timedelta(bodosql_interval_types, spark_info):
    """tests the ntile agregation with timedelta data"""

    fns = ", ".join(
        f"NTILE({x}) OVER (PARTITION BY B ORDER BY C) as NTILE_{x}" for x in [1, 3, 100]
    )

    query = f"select A, B, C, {fns} from table1 ORDER BY B, C"
    check_query(
        query,
        bodosql_interval_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        convert_columns_timedelta=[
            "A",
            "B",
            "C",
        ],
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_ntile_string(bodosql_string_types, spark_info):
    """tests the ntile agregation with string data"""

    fns = ", ".join(
        f"NTILE({x}) OVER (PARTITION BY B ORDER BY C) as NTILE_{x}" for x in [1, 3, 100]
    )

    query = f"select A, B, C, {fns} from table1 ORDER BY B, C"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


@pytest.mark.slow
def test_ntile_binary(bodosql_binary_types, spark_info):
    """tests the ntile agregation with binary data"""
    """NOTE: doesn't currently run, as bodosql_binary_types fixture is skipped"""

    fns = ", ".join(
        f"NTILE({x}) OVER (PARTITION BY B ORDER BY C) as NTILE_{x}" for x in [1, 3, 100]
    )

    query = f"select A, B, C, {fns} from table1 ORDER BY B, C"
    check_query(
        query,
        bodosql_binary_types,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
    )


def test_first_value_fusion(basic_df, spark_info):
    import copy

    new_ctx = copy.deepcopy(basic_df)
    new_ctx["table1"]["D"] = new_ctx["table1"]["A"] + 10
    new_ctx["table1"]["E"] = new_ctx["table1"]["A"] * 2

    window = "(PARTITION BY B ORDER BY C)"

    query = f"select FIRST_VALUE(A) OVER {window}, FIRST_VALUE(D) OVER {window}, FIRST_VALUE(E) OVER {window} from table1"

    codegen = check_query(
        query,
        new_ctx,
        spark_info,
        check_dtype=False,
        check_names=False,
        only_jit_1DVar=True,
        return_codegen=True,
    )["pandas_code"]

    # Check that we only create one lambda function. If we didn't perform loop fusion, there would be three.
    assert codegen.count("def __bodo_dummy___sql_windowed_apply_fn") == 1


def test_first_value_optimized(spark_info):
    """
    Tests for an optimization with first_value when the
    window results in copying the first value of the group into
    every entry.
    """
    table = pd.DataFrame(
        {
            "A": [1, 2] * 10,
            "B": ["A", "B", "C", "D", "E"] * 4,
            "C": ["cq", "e22e", "r32", "#2431d"] * 5,
        }
    )
    ctx = {"table1": table}
    query = f"select FIRST_VALUE(C) OVER (PARTITION BY B ORDER BY A) as tmp from table1"
    check_query(
        query,
        ctx,
        spark_info,
        check_dtype=False,
    )


def test_last_value_optimized(spark_info):
    """
    Tests for an optimization with last_value when the
    window results in copying the last value of the group into
    every entry.
    """
    table = pd.DataFrame(
        {
            "A": [1, 2] * 10,
            "B": ["A", "B", "C", "D", "E"] * 4,
            "C": ["cq", "e22e", "r32", "#2431d"] * 5,
        }
    )
    ctx = {"table1": table}
    query = f"select LAST_VALUE(C) OVER (PARTITION BY B ORDER BY A ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) as tmp from table1"
    check_query(
        query,
        ctx,
        spark_info,
        check_dtype=False,
    )


# @pytest.mark.skip(
#     "specifying non constant arg1 for lead/lag is not supported in spark, but currently allowed in Calcite. Can revisit this later if needed for a customer"
# )
# def test_lead_lag_variable_len(basic_df, lead_or_lag, spark_info, memory_leak_check):
#     """tests the lead and lag agregation functions"""

#     query = f"select A, B, C, {lead_or_lag}(A, B) OVER (PARTITION BY B ORDER BY C) AS LEAD_LAG_COL from table1 ORDER BY B, C"

#     cols_to_cast = [("LEAD_LAG_COL", "float64")]
#     check_query(
#         query,
#         basic_df,
#         spark_info,
#         check_dtype=False,
#         check_names=False,
#         spark_output_cols_to_cast=cols_to_cast,
#         only_jit_1DVar=True,
#     )


# @pytest.mark.skip(
#     """TODO: Spark requires frame bound to be literal, Calcite does not have this restriction.
#     I think that adding this capability should be fairly easy, should it be needed in the future"""
# )
# def test_windowed_agg_nonconstant_values(
#     basic_df,
#     numeric_agg_funcs_subset,
#     over_clause_bounds,
#     spark_info,
#     memory_leak_check,
# ):
#     """Tests windowed agregations works when performing agregations, sorting by, and bounding by non constant values"""

#     # doing an orderby and calculating extra rows in the query so it's easier to tell what the error is by visual comparison
#     query = f"select A, B, C, (A + B + C) as AGG_SUM, (C + B) as ORDER_SUM, {numeric_agg_funcs_subset}(A + B + C) OVER (PARTITION BY B ORDER BY (C+B) ASC ROWS BETWEEN A PRECEDING AND C FOLLOWING) as WINDOW_AGG FROM table1 ORDER BY B, C"

#     # spark windowed min/max on integers returns an integer col.
#     # pandas rolling min/max on integer series returns a float col
#     # (and the method that we currently use returns a float col)
#     cols_to_cast = [("WINDOW_AGG", "float64")]
#     check_query(
#         query,
#         basic_df,
#         spark_info,
#         sort_output=False,
#         check_dtype=False,
#         check_names=False,
#         spark_output_cols_to_cast=cols_to_cast,
#         only_jit_1DVar=True,
#     )


# Some problematic queries that will need to be dealt with eventually:
# "SELECT CASE WHEN A > 1 THEN A * SUM(D) OVER (ORDER BY A ROWS BETWEEN 1 PRECEDING and 1 FOLLOWING) ELSE -1 END from table1"
# "SELECT MAX(A) OVER (ORDER BY A ROWS BETWEEN A PRECEDING and 1 FOLLOWING) from table1"
# "SELECT MAX(A) OVER (ORDER BY A+D ROWS BETWEEN CURRENT ROW and 1 FOLLOWING) from table1"
# SELECT 1 + MAX(A) OVER (ORDER BY A ROWS BETWEEN CURRENT ROW and 1 FOLLOWING) from table1
