import re
from pathlib import Path

import pandas as pd
import pytest

from luc import main

TEST_DIR = Path(__file__).parent / "test_data"  # absolute


def _sort_dataframe(df):
    # sort column order
    df = df.sort_index(axis=1)
    # in case order changes
    df = df.sort_values(df.columns.to_list())
    return df


@pytest.fixture
def comp_df():
    df = pd.read_csv(TEST_DIR / "Test Output.csv")
    df = df.set_index("artist")
    return _sort_dataframe(df)


def _assert_frames_equal(df1, df2):
    comp = df1.compare(df2)
    assert comp.shape[0] == 0


print(TEST_DIR)


def test_luc_with_abs_str(comp_df):
    print(TEST_DIR)
    msg = re.escape(
        r"Supposed to exclude twenty (feat. stevan) by "
        "stevan for apple but selection is not present."
    )
    with pytest.warns(UserWarning, match=msg) as record:
        df = main(
            date_dir=TEST_DIR, song_sheet_name="Test Song Sheet.csv", return_df=True
        )
    # make sure warning is propogated once and only once
    assert len(record) == 1
    df = _sort_dataframe(df)
    _assert_frames_equal(df, comp_df)


def test_luc_with_rel_str():
    pass


def test_luc_with_abs_path():
    pass


def test_luc_with_rel_path():
    pass
