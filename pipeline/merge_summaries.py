"""
Merge chunk-level summary progress files into one enriched CSV.

Globs summaries_progress_*.json, merges results, and writes the final
enriched_researcher_papers.csv via generate_summaries.write_enriched_csv().

Usage:
    python merge_summaries.py --input combined.csv --output enriched.csv --progress-dir ./output
"""

import argparse
import glob
import json
import sys
from pathlib import Path

from generate_summaries import group_by_researcher, write_enriched_csv


def merge_progress_files(progress_dir: Path) -> dict[str, dict]:
    pattern = str(progress_dir / "summaries_progress_*.json")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No progress files found matching {pattern}", file=sys.stderr)
        sys.exit(1)

    merged: dict[str, dict] = {}
    for f in files:
        print(f"  Loading {Path(f).name}")
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            merged.update(data)

    print(f"Merged {len(merged)} researchers from {len(files)} progress files")
    return merged


def main():
    parser = argparse.ArgumentParser(description="Merge summary progress files into enriched CSV")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input combined CSV")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output enriched CSV")
    parser.add_argument("--progress-dir", type=Path, required=True, help="Directory containing summaries_progress_*.json files")
    args = parser.parse_args()

    groups = group_by_researcher(args.input)
    print(f"Loaded {len(groups)} researchers from CSV")

    merged = merge_progress_files(args.progress_dir)

    missing = [sid for sid in groups if sid not in merged]
    if missing:
        print(f"WARNING: {len(missing)} researchers have no summaries (will use empty strings)")
        for sid in missing[:10]:
            name = groups[sid]["profile"]["name"]
            print(f"  - {name} ({sid})")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

    write_enriched_csv(args.output, groups, merged)
    print(f"Output: {args.output}")
    print(f"Total researchers: {len(groups)}, with summaries: {len(groups) - len(missing)}")


if __name__ == "__main__":
    main()
