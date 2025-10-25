#!/usr/bin/env python3
# scripts/aggregate_reports.py
import os
from glob import glob

OUT = "reports/PhaseB_Aggregated.md"
parts = sorted(glob("reports/B.*_*.md") + glob("reports/*PhaseB*.md") + glob("reports/Audit_*.md"))
with open(OUT, "w") as out:
    out.write("# Phase B Aggregated Report\n\n")
    for p in parts:
        out.write(f"## From {p}\n\n")
        out.write("```\n")
        try:
            with open(p, "r") as fh:
                out.write(fh.read())
        except Exception as e:
            out.write(f"ERROR reading {p}: {e}\n")
        out.write("\n```\n\n")
print("Wrote aggregated report:", OUT)
