"""Build the QC report website into dist/.

Run it with:   python src/report.py
Then open dist/index.html in your browser.
"""

import html
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw charts to files, without opening a window
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qc import DATA_FILE, problems_for  # noqa: E402

DIST = Path(__file__).resolve().parent.parent / "dist"


def classify_purity(ratio):
    """A260/280 of about 1.8 to 2.0 means clean nucleic acid."""
    if ratio < 1.8:
        return "low"
    if ratio <= 2.0:
        return "pass"
    return "high"


def summary_by_type(df):
    """One row per sample type: how many samples, mean concentration, and how many passed purity."""
    df = df.assign(purity=df["a260_280"].map(classify_purity))
    summary = df.groupby("sample_type").agg(
        samples=("sample_id", "count"),
        mean_concentration_ng_ul=("concentration_ng_ul", "mean"),
        purity_pass=("purity", lambda s: int((s == "pass").sum())),
    )
    summary["mean_concentration_ng_ul"] = summary["mean_concentration_ng_ul"].round(1)
    return summary.reset_index()


def load():
    df = pd.read_csv(DATA_FILE, dtype=str)
    problems = problems_for(df)
    if problems:
        raise ValueError("refusing to build: run python src/qc.py to see the problems")
    for col in ["ct_value", "concentration_ng_ul", "a260_280"]:
        df[col] = pd.to_numeric(df[col])
    return df


def draw_charts(df, out_dir):
    fig, ax = plt.subplots(figsize=(6, 3.5))
    df.boxplot(column="concentration_ng_ul", by="sample_type", ax=ax, grid=False)
    ax.set_title("DNA concentration by sample type")
    ax.set_xlabel("")
    ax.set_ylabel("ng/µL")
    fig.suptitle("")
    fig.tight_layout()
    fig.savefig(out_dir / "concentration.png", dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    df.boxplot(column="ct_value", by="gene", ax=ax, grid=False)
    ax.set_title("qPCR Ct value by gene")
    ax.set_xlabel("")
    ax.set_ylabel("Ct")
    fig.suptitle("")
    fig.tight_layout()
    fig.savefig(out_dir / "ct_by_gene.png", dpi=120)
    plt.close(fig)


def footer_text():
    run = os.environ.get("GITHUB_RUN_NUMBER")
    sha = os.environ.get("GITHUB_SHA", "")[:7]
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if run:
        return f"Built by pipeline run #{run} from commit {sha} on {when}"
    return f"Built on your computer on {when}"


def build():
    df = load()
    DIST.mkdir(exist_ok=True)
    draw_charts(df, DIST)

    flagged = df[df["a260_280"].map(classify_purity) != "pass"]
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab QC report</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
  table {{ border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ccc; padding: .4rem .7rem; text-align: left; }}
  th {{ background: #f3f3f3; }}
  img {{ max-width: 100%; }}
  footer {{ margin-top: 3rem; color: #777; font-size: .9rem; }}
</style>
</head>
<body>
<h1>Lab QC report</h1>
<p>{len(df)} samples from {html.escape(df["collection_date"].min())} to {html.escape(df["collection_date"].max())}.</p>

<h2>Summary by sample type</h2>
{summary_by_type(df).to_html(index=False)}

<h2>Samples to re-check (A260/280 outside 1.8&ndash;2.0)</h2>
{flagged[["sample_id", "sample_type", "a260_280"]].to_html(index=False) if len(flagged) else "<p>None.</p>"}

<h2>Charts</h2>
<img src="concentration.png" alt="Box plot of DNA concentration by sample type">
<img src="ct_by_gene.png" alt="Box plot of qPCR Ct value by gene">

<footer>{html.escape(footer_text())}</footer>
</body>
</html>
"""
    (DIST / "index.html").write_text(page, encoding="utf-8")
    print(f"Built {DIST / 'index.html'} from {len(df)} samples.")


if __name__ == "__main__":
    build()
