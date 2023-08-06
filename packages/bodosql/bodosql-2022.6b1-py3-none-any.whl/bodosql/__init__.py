import bodosql.context_ext

# Import BodoSQL types
import bodosql.bodosql_types.table_path

# Import BodoSQL libs
import bodosql.libs.regex
import bodosql.libs.null_handling
import bodosql.libs.numeric_helpers
import bodosql.libs.substring_helper
import bodosql.libs.string_helpers
import bodosql.libs.two_op_string_fn_helpers
import bodosql.libs.LR_pad_string
import bodosql.libs.substring_helper
import bodosql.libs.nullchecked_logical_operators
import bodosql.libs.datetime_wrappers
import bodosql.libs.simple_wrappers
import bodosql.libs.sql_operators
import bodosql.libs.sql_datetime_helpers
import bodosql.libs.ntile_helper

# Import the library, throwing an error if it does not exist
import os

# TODO: put the generated library path in a global variable somewhere that is commonly accessible
GENERATED_LIB_FILE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "libs", "generated_lib.py"
)
if os.path.isfile(GENERATED_LIB_FILE_PATH):
    import bodosql.libs.generated_lib
else:
    raise Exception(
        "Error durring module import, did not find the generated library in the expected location: bodosql/libs/generated_lib.py"
    )

from bodosql.context import BodoSQLContext
from bodosql.bodosql_types.table_path import TablePath, TablePathType


from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
