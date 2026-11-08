import pandas as pd

from qc import problems_for

GOOD_ROW = {
    "sample_id": "S001",
    "collection_date": "2026-09-03",
    "sample_type": "blood",
    "gene": "GAPDH",
    "ct_value": "22.5",
    "concentration_ng_ul": "40.0",
    "a260_280": "1.85",
}


def table(*rows):
    return pd.DataFrame(list(rows), dtype=str)


def test_good_row_has_no_problems():
    assert problems_for(table(GOOD_ROW)) == []


def test_negative_concentration_is_a_problem():
    problems = problems_for(table({**GOOD_ROW, "concentration_ng_ul": "-5"}))
    assert problems == ["S001: concentration_ng_ul must be a number above 0 (got -5)"]


def test_unknown_sample_type_is_a_problem():
    problems = problems_for(table({**GOOD_ROW, "sample_type": "urine"}))
    assert len(problems) == 1
    assert "sample_type must be one of" in problems[0]


def test_ct_value_out_of_range_is_a_problem():
    assert len(problems_for(table({**GOOD_ROW, "ct_value": "45"}))) == 1


def test_not_a_real_date_is_a_problem():
    assert len(problems_for(table({**GOOD_ROW, "collection_date": "2026-02-30"}))) == 1


def test_duplicate_sample_id_is_a_problem():
    problems = problems_for(table(GOOD_ROW, GOOD_ROW))
    assert problems == ["S001: sample_id is used more than once"]


def test_missing_column_is_a_problem():
    df = table(GOOD_ROW).drop(columns=["gene"])
    assert problems_for(df) == ["missing column(s): gene"]
