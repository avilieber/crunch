from pathlib import Path

import pytest
import pandas as pd

from luc import main

TEST_DIR = Path(__file__).parent / 'test_data'

def _sort_dataframe(df):
    df = df.sort_index(axis=1)
    df = df.sort_values(df.columns.to_list())
    return df

@pytest.fixture
def comp_df():
    df = pd.read_csv(TEST_DIR / 'Test Output.csv')
    return _sort_dataframe(df)

def test_luc(comp_df):
    df = main(TEST_DIR, 'Test Song Sheet.csv', return_df=True)
    df = _sort_dataframe(df)
    assert df.compare(comp_df).shape[0] == 0