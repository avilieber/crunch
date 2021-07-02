import re
from pathlib import Path

import pandas as pd
import pytest

from crunch import OUTPUT_NAME, SONG_SHEET_NAME, main

TEST_DIR = Path(__file__).parent / "test_data"  # absolute


def _sort_dataframe(df):
    # sort column order
    df = df.sort_index(axis=1)
    # in case order changes
    df = df.sort_values(df.columns.to_list())
    return df


@pytest.fixture
def comp_df():
    df = pd.read_csv(TEST_DIR / f"true-{OUTPUT_NAME}")
    df = df.set_index("artist")
    return _sort_dataframe(df)


def _assert_frames_equal(df1, df2):
    comp = df1.compare(df2)
    assert comp.shape[0] == 0


# test params
test_dir_abs_path = TEST_DIR
test_dir_abs_str = str(TEST_DIR)
test_dir_rel_path = test_dir_abs_path.relative_to(test_dir_abs_path.parent)
test_dir_rel_str = str(test_dir_rel_path)
params = [
    test_dir_abs_path,
    test_dir_abs_str,
    # test_dir_rel_path,
    # test_dir_rel_str
]


@pytest.mark.parametrize("filepath", params)
def test_luc_with_abs_str(comp_df, filepath):

    msg = re.escape(
        r"Supposed to exclude twenty (feat. stevan) by "
        "stevan for apple but selection is not present."
    )
    with pytest.warns(UserWarning, match=msg) as record:
        df = main(
            date_dir=filepath, song_sheet_name=f"true-{SONG_SHEET_NAME}", return_df=True
        )
    # make sure warning is propogated once and only once
    assert len(record) == 1
    df = _sort_dataframe(df)
    _assert_frames_equal(df, comp_df)
