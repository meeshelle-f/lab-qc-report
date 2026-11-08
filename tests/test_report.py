import pandas as pd

from report import classify_purity, summary_by_type


def test_purity_inside_the_range_passes():
    assert classify_purity(1.9) == "pass"


def test_purity_edges_of_the_range_pass():
    assert classify_purity(1.8) == "pass"
    assert classify_purity(2.0) == "pass"


def test_purity_below_the_range_is_low():
    assert classify_purity(1.6) == "low"


def test_purity_above_the_range_is_high():
    assert classify_purity(2.1) == "high"


def test_summary_counts_samples_and_purity_passes():
    df = pd.DataFrame(
        {
            "sample_id": ["S001", "S002", "S003"],
            "sample_type": ["blood", "blood", "saliva"],
            "concentration_ng_ul": [40.0, 60.0, 10.0],
            "a260_280": [1.9, 1.5, 2.0],
        }
    )
    summary = summary_by_type(df).set_index("sample_type")
    assert summary.loc["blood", "samples"] == 2
    assert summary.loc["blood", "mean_concentration_ng_ul"] == 50.0
    assert summary.loc["blood", "purity_pass"] == 1
    assert summary.loc["saliva", "purity_pass"] == 1
