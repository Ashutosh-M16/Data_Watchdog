import pandas as pd
from src.ingestion.loader import load_data


def test_load_sample():
    df, meta = load_data('data/sample/sample_business_data.csv')
    assert df.shape[0] > 0
    assert 'Revenue' in df.columns
