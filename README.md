# lab-qc-report
![Pipeline](https://github.com/meeshelle-f/lab-qc-report/actions/workflows/pipeline.yml/badge.svg)

Build a pipeline that checks a qPCR sample sheet, tests the analysis code, builds an HTML QC report with charts, and publishes it to GitHub Pages. It is the same test → build → deploy idea as the learning-reviews lesson, using lab data and Python instead of reviews and Node.

## Goal 
Data analyst adds one row of data, and the pipeline handles everything else. A good row goes all the way to the live report. A bad row, or a code bug, gets stopped at the test step, so the live report is never affected.

## How it works

```mermaid
flowchart LR
    A["You: add a sample row"] --> B
    subgraph P["GitHub Actions pipeline (automatic)"]
        B["Test: QC + unit tests"] --> C["Build: make the report"]
        C --> D["Deploy: live on Pages"]
    end
    B -. "bad data or a bug" .-> X["Stops here, live site safe"]
```
