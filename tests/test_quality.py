import pandas as pd
from src.preprocessing import cleaner


def test_quality_report():
    df = pd.read_csv('data/sample/sample_business_data.csv')
    cleaned, log, report = cleaner.clean_data(df.copy())
    assert 'overall_quality' in report
    assert 0 <= report['overall_quality'] <= 100
