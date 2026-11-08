"""Quality checks for data/samples.csv.

Run it with:   python src/qc.py
It prints one line per problem, and exits with an error if it finds any.
That error is what makes the pipeline's test job fail.
"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "samples.csv"

REQUIRED_COLUMNS = [
    "sample_id",
    "collection_date",
    "sample_type",
    "gene",
    "ct_value",
    "concentration_ng_ul",
    "a260_280",
]
SAMPLE_TYPES = {"blood", "saliva", "tissue"}
GENES = {"GAPDH", "ACTB", "BRCA1", "TP53"}


def problems_for(df):
    """Return a list of problems in the table. An empty list means the data is valid."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return [f"missing column(s): {', '.join(missing)}"]

    problems = []

    duplicated = df["sample_id"][df["sample_id"].duplicated()]
    for sample_id in duplicated:
        problems.append(f"{sample_id}: sample_id is used more than once")

    for row_number, row in df.iterrows():
        label = row["sample_id"] if isinstance(row["sample_id"], str) else f"row {row_number + 2}"

        if not (isinstance(row["sample_id"], str) and row["sample_id"].startswith("S")):
            problems.append(f"{label}: sample_id must look like S001")

        parsed = pd.to_datetime(row["collection_date"], format="%Y-%m-%d", errors="coerce")
        if pd.isna(parsed):
            problems.append(f"{label}: collection_date must be a real date, like 2026-09-03")
        elif parsed.date() > date.today():
            problems.append(f"{label}: collection_date is in the future")

        if row["sample_type"] not in SAMPLE_TYPES:
            problems.append(
                f"{label}: sample_type must be one of {', '.join(sorted(SAMPLE_TYPES))}"
                f" (got {row['sample_type']})"
            )

        if row["gene"] not in GENES:
            problems.append(f"{label}: gene must be one of {', '.join(sorted(GENES))} (got {row['gene']})")

        ct = pd.to_numeric(row["ct_value"], errors="coerce")
        if pd.isna(ct) or not 10 <= ct <= 40:
            problems.append(f"{label}: ct_value must be a number from 10 to 40 (got {row['ct_value']})")

        conc = pd.to_numeric(row["concentration_ng_ul"], errors="coerce")
        if pd.isna(conc) or conc <= 0:
            problems.append(
                f"{label}: concentration_ng_ul must be a number above 0 (got {row['concentration_ng_ul']})"
            )

        ratio = pd.to_numeric(row["a260_280"], errors="coerce")
        if pd.isna(ratio) or not 0 < ratio <= 3:
            problems.append(f"{label}: a260_280 must be a number above 0 and at most 3 (got {row['a260_280']})")

    return problems


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    problems = problems_for(df)
    if problems:
        print(f"Found {len(problems)} problem(s) in {DATA_FILE.name}:")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)
    print(f"{DATA_FILE.name}: {len(df)} samples, no problems found.")


if __name__ == "__main__":
    main()
