import pandas as pd
import pytest

from bodosql.tests.string_ops_common import *  # noqa
from bodosql.tests.utils import check_query


def test_substring_negative(
    bodosql_string_types, spark_info, substring_fn_names, memory_leak_check
):
    """tests the correctness of the substring, mid, and substr functions with negative starting indexes"""

    query = f"select {substring_fn_names}(A, -4, 4), {substring_fn_names}(B, -2, 1), {substring_fn_names}(C, -1, 2) from table1"
    spark_query = "select substring(A, -4, 4), substring(B, -2, 1), substring(C, -1, 2) from table1"

    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
        equivalent_spark_query=spark_query,
    )


def test_substring_edgecases(
    bodosql_string_types, spark_info, substring_fn_names, memory_leak_check
):
    """test that substring, mid, and substr properly handles edgecases"""

    # I think 0 indexing with spark is undefined
    # At the very least, their result is very different from standard mysql, which is to return empty string
    # https://www.w3schools.com/sql/trymysql.asp?filename=trysql_func_mysql_substring
    query = f"select {substring_fn_names}(A, 0, 4), {substring_fn_names}(B, 2, -2), {substring_fn_names}(C, 3, 0) from table1"
    spark_query = "select substring(A, 1, 0), substring(B, 2, -2), substring(C, 3, 0) as alias from table1"

    check_query(
        query,
        bodosql_string_types,
        spark_info,
        equivalent_spark_query=spark_query,
        check_names=False,
    )


def test_substring_int_args_cols(
    bodosql_string_types, basic_df, spark_info, substring_fn_names, memory_leak_check
):
    """tests that substring, mid, and substr work when the start and len arguments are columns"""
    new_ctx = {"t1": bodosql_string_types["table1"], "t2": basic_df["table1"]}

    query = f"select {substring_fn_names}(t1.A, t2.A, 4), {substring_fn_names}(t1.B, 1, t2.B), {substring_fn_names}(t1.C, t2.A, t2.B) from t1, t2"
    spark_query = "select substring(t1.A, t2.A, 4), substring(t1.B, 1, t2.B), substring(t1.C, t2.A, t2.B) from t1, t2"

    check_query(
        query,
        new_ctx,
        spark_info,
        check_names=False,
        equivalent_spark_query=spark_query,
    )


def test_substring_int_args_cols(
    bodosql_string_types, basic_df, spark_info, substring_fn_names, memory_leak_check
):
    """tests that substring, mid, and substr work when the start and len arguments are columns"""
    new_ctx = {"t1": bodosql_string_types["table1"], "t2": basic_df["table1"]}

    query = f"select {substring_fn_names}(t1.A, t2.A, 4), {substring_fn_names}(t1.B, 1, t2.B), {substring_fn_names}(t1.C, t2.A, t2.B) from t1, t2"
    spark_query = "select substring(t1.A, t2.A, 4), substring(t1.B, 1, t2.B), substring(t1.C, t2.A, t2.B) from t1, t2"

    check_query(
        query,
        new_ctx,
        spark_info,
        check_names=False,
        equivalent_spark_query=spark_query,
    )


def test_substring_scalar_string(
    bodosql_string_types, spark_info, substring_fn_names, memory_leak_check
):
    """tests that substring, mid, and substr works when the string argument is a scalar"""
    query = f"select CASE WHEN {substring_fn_names}(A,1,2) > 'A' THEN {substring_fn_names}(B,1,4) ELSE {substring_fn_names}(B,1,10) END from table1"
    spark_query = "select CASE WHEN substring(A,1,2) > 'A' THEN substring(B,1,4) ELSE substring(B,1,10) END from table1"

    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
        only_python=True,
        equivalent_spark_query=spark_query,
    )


def test_substring_null_vals(substring_fn_names, spark_info, memory_leak_check):
    """tests that substring, mid, and substr works on nullable values"""
    # Spark's behavior with arg0 = null is to treat it as equivalent to 0.
    # therefore, I'm just going to manually set the expected output

    int_data = pd.DataFrame(
        {
            "A": pd.Series([2, 2, None, None], dtype="Int32"),
            "B": pd.Series([4, None, 6, None], dtype="Int32"),
        }
    )
    str_data = pd.DataFrame(
        {
            "A": ["HELLO", None] * 4,
        }
    )

    expected_output = pd.DataFrame(
        {
            "Unkown_name": ["ELLO", None, None, None, None, None, None, None] * 4,
        }
    )

    new_ctx = {"table1": str_data, "table2": int_data}
    query = (
        f"select {substring_fn_names}(table1.A,table2.A,table2.B) from table1, table2"
    )

    check_query(
        query,
        new_ctx,
        spark_info,
        check_names=False,
        expected_output=expected_output,
    )


def test_concat_operator_cols(bodosql_string_types, spark_info, memory_leak_check):
    """Checks that the concat operator is working for columns"""
    query = "select A || B || 'scalar' || C from table1"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


@pytest.mark.slow
def test_concat_operator_scalars(bodosql_string_types, spark_info, memory_leak_check):
    """Checks that the concat operator is working for scalar values"""
    query = (
        "select CASE WHEN A > 'A' THEN B || ' case1' ELSE C || ' case2' END from table1"
    )
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


def test_concat_fn_cols(bodosql_string_types, spark_info, memory_leak_check):
    """Checks that the concat function is working for columns"""
    # Technically, in MYSQL, it's valid to pass only one arg to Concat
    # However, defining a function that takes at least 1 string arguement seems to
    # cause validateQuery in the RelationalAlgebraGenerator to throw an index out of
    # bounds error and I don't think calling Concat on one string is a common use case
    query = "select CONCAT(A, B, 'scalar', C) from table1"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


@pytest.mark.slow
def test_concat_fn_scalars(bodosql_string_types, spark_info, memory_leak_check):
    """Checks that the concat function is working for scalar values"""
    query = "select CASE WHEN A > 'A' THEN CONCAT(B, ' case1') ELSE CONCAT(C, ' case2') END from table1"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


def test_concat_ws_cols(bodosql_string_types, spark_info, memory_leak_check):
    """Checks that the concat_ws function is working for columns"""
    query = "select CONCAT_WS('_', A, B, C), CONCAT_WS(A, B) from table1"
    spark_query = "select CONCAT(A, '_', B, '_', C), B from table1"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
        equivalent_spark_query=spark_query,
    )


def test_string_fns_cols(
    spark_info, bodosql_string_fn_testing_df, string_fn_info, memory_leak_check
):
    """tests that the specified string functions work on columns"""
    bodo_fn_name = string_fn_info[0]
    arglistString = ", ".join(string_fn_info[1])
    bodo_fn_call = f"{bodo_fn_name}({arglistString})"

    query = f"SELECT {bodo_fn_call} FROM table1"

    if bodo_fn_name in BODOSQL_TO_PYSPARK_FN_MAP:
        spark_fn_name = BODOSQL_TO_PYSPARK_FN_MAP[bodo_fn_name]
        spark_fn_call = f"{spark_fn_name}({arglistString})"
        spark_query = f"SELECT {spark_fn_call} FROM table1"
    else:
        spark_query = None

    # Trim fn's not supported on columns. see BE-965
    if bodo_fn_name in {"LTRIM", "RTRIM", "TRIM"}:
        return

    check_query(
        query,
        bodosql_string_fn_testing_df,
        spark_info,
        check_names=False,
        check_dtype=False,
        equivalent_spark_query=spark_query,
    )


@pytest.mark.slow
def test_concat_ws_scalars(bodosql_string_types, spark_info, memory_leak_check):
    """Checks that the concat_ws function is working for scalar values"""
    query = "select CASE WHEN A > 'A' THEN CONCAT_WS(' case1 ', B, C, A) ELSE CONCAT_WS(A,B,C) END from table1"
    spark_query = "select CASE WHEN A > 'A' THEN CONCAT(B, ' case1 ', C, ' case1 ', A) ELSE CONCAT(B, A, C) END from table1"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
        equivalent_spark_query=spark_query,
    )


def test_string_fns_scalars(
    spark_info, bodosql_string_fn_testing_df, string_fn_info, memory_leak_check
):
    """tests that the specified string functions work on Scalars"""
    bodo_fn_name = string_fn_info[0]
    arglistString = ", ".join(string_fn_info[1])
    bodo_fn_call = f"{bodo_fn_name}({arglistString})"
    retval_1 = string_fn_info[2][0]
    retval_2 = string_fn_info[2][1]

    query = f"SELECT CASE WHEN {bodo_fn_call} = {retval_1} THEN {retval_2} ELSE {bodo_fn_call} END FROM table1"
    if bodo_fn_name in BODOSQL_TO_PYSPARK_FN_MAP:
        spark_fn_name = BODOSQL_TO_PYSPARK_FN_MAP[bodo_fn_name]
        spark_fn_call = f"{spark_fn_name}({arglistString})"
        spark_query = f"SELECT CASE WHEN {spark_fn_call} = {retval_1} THEN {retval_2} ELSE {spark_fn_call} END FROM table1"
    else:
        spark_query = None

    check_query(
        query,
        bodosql_string_fn_testing_df,
        spark_info,
        check_names=False,
        check_dtype=False,
        equivalent_spark_query=spark_query,
    )


@pytest.mark.skipif(
    bodo_version_older(2022, 6, 0),
    reason="Requires next mini-release for engine changes to support the LPAD/RPAD kernels",
)
@pytest.mark.parametrize(
    "query",
    [
        pytest.param(
            "SELECT LPAD(strings_null_1, mixed_ints_null, strings_null_2) from table1",
            id="LPAD_all_vector",
        ),
        pytest.param(
            "SELECT LPAD(strings_null_1, mixed_ints_null, ' ') from table1",
            id="LPAD_scalar_str",
        ),
        pytest.param(
            "SELECT LPAD(strings_null_1, 20, strings_null_2) from table1",
            id="LPAD_scalar_int",
            marks=pytest.mark.slow,
        ),
        pytest.param(
            "SELECT LPAD('A', 25, ' ') from table1",
            id="LPAD_all_scalar",
            marks=pytest.mark.slow,
        ),
        pytest.param(
            "SELECT RPAD(strings_null_1, mixed_ints_null, strings_null_2) from table1",
            id="RPAD_all_vector",
        ),
        pytest.param(
            "SELECT RPAD(strings_null_1, mixed_ints_null, 'ABC') from table1",
            id="RPAD_scalar_str",
            marks=pytest.mark.slow,
        ),
        pytest.param(
            "SELECT RPAD(strings_null_1, 25, strings_null_2) from table1",
            id="RPAD_scalar_int",
            marks=pytest.mark.slow,
        ),
        pytest.param(
            "SELECT RPAD('words', 25, strings_null_2) from table1",
            id="RPAD_two_scalar",
            marks=pytest.mark.slow,
        ),
        pytest.param(
            "SELECT LPAD('B', 20, '_$*') from table1",
            id="RPAD_all_scalar",
            marks=pytest.mark.slow,
        ),
    ],
)
def test_string_fns_scalar_vector(
    query, spark_info, bodosql_string_fn_testing_df, memory_leak_check
):
    check_query(
        query,
        bodosql_string_fn_testing_df,
        spark_info,
        check_names=False,
        check_dtype=False,
    )


def test_substring_index_col_scalar_scalar(
    bodosql_string_types, spark_info, memory_leak_check
):
    """tests the correctness of the substring index function for the common case, where the arguments are col scalar scalar"""
    check_query(
        "select substring_index(A, 'el', 2), substring_index(B, 'e', -2), substring_index(C, ' ', 1) from table1",
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


@pytest.mark.slow
def test_substring_index_edgecases(bodosql_string_types, spark_info, memory_leak_check):
    """test that substring index properly handles edgecases"""
    query = "select substring_index(A, '', 2), substring_index(B, 'e', 0), substring_index(C, 'e', -10) from table1"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


def test_substring_index_other_args_cols(
    bodosql_string_types, basic_df, spark_info, memory_leak_check
):
    """tests that substring index works when the delimiter and number arguments are columns"""
    new_ctx = {"t1": bodosql_string_types["table1"], "t2": basic_df["table1"]}
    query = "select substring_index('hello world, how are you today?', t1.B, 1), substring_index('hello world, how are you today?', 'e', t2.A) from t1, t2"

    check_query(
        query,
        new_ctx,
        spark_info,
        check_names=False,
    )


@pytest.mark.slow
def test_substring_index_scalars(bodosql_string_types, spark_info, memory_leak_check):
    """tests that substring index works when all the arguments are scalars"""
    query = "select CASE WHEN substring_index(A,'e',2) > 'A' THEN substring_index(B,'e', -1) ELSE substring_index(C,'e', -1) END from table1"
    check_query(
        query,
        bodosql_string_types,
        spark_info,
        check_names=False,
    )


@pytest.mark.skip(
    "BE-967, behavior of float to string casts within JIT is different from standard python."
)
def test_format(spark_info, bodosql_string_fn_testing_df, memory_leak_check):
    """tests mysql format. Separate test needed as the spark version does not allow bigint to be passed as a second argument,
    and spark seems to interpret all integer pandas dataframes as bigint, see BS-421"""

    new_df = pd.DataFrame(
        {
            "mixed_floats": bodosql_string_fn_testing_df["table1"]["mixed_floats"],
            "positive_ints": bodosql_string_fn_testing_df["table1"]["positive_ints"],
            "spark_format_string": [
                100 * "#" + "." + "#" * x
                for x in bodosql_string_fn_testing_df["table1"]["positive_ints"]
            ],
        }
    )

    new_ctx = {"table1": new_df}
    col_query = "SELECT FORMAT(mixed_floats, positive_ints) from table1"
    col_query_spark = (
        "SELECT FORMAT_NUMBER(mixed_floats, spark_format_string) from table1"
    )

    check_query(
        col_query,
        new_ctx,
        spark_info,
        check_names=False,
        check_dtype=False,
        equivalent_spark_query=col_query_spark,
    )

    scalar_query = "SELECT CASE FORMAT(mixed_floats, positive_ints) = 'a' then '' else FORMAT(mixed_floats, positive_ints) END from table1"
    scalar_query_spark = "SELECT CASE FORMAT_NUMBER(mixed_floats, spark_format_string) = 'a' then '' else FORMAT_NUMBER(mixed_floats, positive_ints) END from table1"
    check_query(
        scalar_query,
        new_ctx,
        spark_info,
        check_names=False,
        check_dtype=False,
        equivalent_spark_query=scalar_query_spark,
    )


def test_strcmp(spark_info, memory_leak_check):
    """tests mysql strcmp. Seperate test needed as the spark version does not allow bigint to be passed as a second argument,
    see BS-421"""

    df = pd.DataFrame({"s": ["a", "b", "c", "be", "bb"]})

    ctx = {"t1": df, "t2": df}

    query1 = "SELECT STRCMP(t1.s, t2.s) from t1, t2"
    expected_output1 = pd.DataFrame(
        {
            # Expected output is an even number of -1 and 1 because join.
            # Order is fixed by sorting
            "name": [0] * 5
            + [-1, 1] * 10
        }
    )

    query2 = "SELECT CASE WHEN STRCMP(s, 'b') = 1 then -2 WHEN STRCMP(s, 'b') = -1 then 2 ELSE 0 END from t1"
    expected_output2 = pd.DataFrame(
        {
            "name": [0, 2, -2, -2, -2],
        }
    )

    check_query(
        query1,
        ctx,
        spark_info,
        check_names=False,
        check_dtype=False,
        expected_output=expected_output1,
    )

    check_query(
        query2,
        ctx,
        spark_info,
        check_names=False,
        check_dtype=False,
        expected_output=expected_output2,
    )
