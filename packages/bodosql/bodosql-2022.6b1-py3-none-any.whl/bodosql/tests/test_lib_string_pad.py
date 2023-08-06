# Copyright (C) 2021 Bodo Inc. All rights reserved.
"""
Test correctness of bodosql.libs.regex functions
"""
import pytest

import bodosql.libs.LR_pad_string


@pytest.mark.slow
def test_LRpad():
    extended_abc = "abc" * 100

    for i in [1, 10, 13, 50]:
        lpad_res = bodosql.libs.LR_pad_string.lpad_scalar("1", i, "abc")
        rpad_res = bodosql.libs.LR_pad_string.rpad_scalar("1", i, "abc")
        assert lpad_res[:-1] == extended_abc[: i - 1]
        assert rpad_res[1:] == extended_abc[: i - 1]

    len_30_string = "abc" * 10
    for i in [0, 30, 13]:
        lpad_res = bodosql.libs.LR_pad_string.lpad_scalar(len_30_string, i, "")
        rpad_res = bodosql.libs.LR_pad_string.lpad_scalar(len_30_string, i, "")
        assert lpad_res == rpad_res and lpad_res == extended_abc[:i]

    for i in [31, 35]:
        lpad_res = bodosql.libs.LR_pad_string.lpad_scalar(len_30_string, i, "")
        rpad_res = bodosql.libs.LR_pad_string.lpad_scalar(len_30_string, i, "")
        assert lpad_res == rpad_res and lpad_res == ""
