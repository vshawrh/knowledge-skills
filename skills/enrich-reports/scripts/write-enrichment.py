#!/usr/bin/env python3
"""Write a validated enrichment JSON file for a single case study.

Usage:
    python write-enrichment.py <case_study_id> \
        --error-signature <regex> \
        --fix-type <type> \
        --generalizable-pattern <text> \
        --prevention-advice <text> \
        --category <category> \
        --tags <tag1> <tag2> ...

Validates all fields before writing. Exits non-zero on validation failure.
"""

import argparse
import json
import re
import sys
from pathlib import Path

VALID_FIX_TYPES = {"code_change", "config_change", "dependency_update", "infra_change", "manual"}
VALID_CATEGORIES = {"dependency", "build-config", "test", "infrastructure", "compatibility", "security"}
CS_ID_PATTERN = re.compile(r"^cs-[a-zA-Z][a-zA-Z0-9-]+-\d{8}$")


def validate(args: argparse.Namespace) -> list[str]:
    errors = []

    if not CS_ID_PATTERN.match(args.case_study_id):
        errors.append(f"Invalid case_study_id format: {args.case_study_id}")

    if not args.error_signature.strip():
        errors.append("error_signature must not be empty")
    else:
        try:
            re.compile(args.error_signature)
        except re.error as exc:
            errors.append(f"error_signature is not a valid regex: {exc}")

    if args.fix_type not in VALID_FIX_TYPES:
        errors.append(f"fix_type must be one of {sorted(VALID_FIX_TYPES)}, got: {args.fix_type}")

    if not args.generalizable_pattern.strip():
        errors.append("generalizable_pattern must not be empty")

    if not args.prevention_advice.strip():
        errors.append("prevention_advice must not be empty")

    if args.category not in VALID_CATEGORIES:
        errors.append(f"category must be one of {sorted(VALID_CATEGORIES)}, got: {args.category}")

    if not args.tags or len(args.tags) < 3 or len(args.tags) > 5:
        errors.append(f"tags must have 3-5 entries, got {len(args.tags or [])}")
    elif any(not t or t != t.lower() for t in args.tags):
        errors.append(f"tags must be non-empty lowercase strings, got: {args.tags}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a validated enrichment JSON file.")
    parser.add_argument("case_study_id", help="Case study ID (e.g., cs-AIPCC-1234-20260801)")
    parser.add_argument("--error-signature", required=True, help="Python regex for the error")
    parser.add_argument("--fix-type", required=True, help="Fix type classification")
    parser.add_argument("--generalizable-pattern", required=True, help="Reusable lesson")
    parser.add_argument("--prevention-advice", required=True, help="Prevention advice")
    parser.add_argument("--category", required=True, help="Category classification")
    parser.add_argument("--tags", required=True, nargs="+", help="3-5 keyword tags")

    args = parser.parse_args()
    errors = validate(args)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    enrichment = {
        "error_signature": args.error_signature,
        "fix_type": args.fix_type,
        "generalizable_pattern": args.generalizable_pattern,
        "prevention_advice": args.prevention_advice,
        "category": args.category,
        "tags": args.tags,
    }

    out_dir = Path("artifacts/enrichments")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.case_study_id}.json"
    out_path.write_text(json.dumps(enrichment, indent=2) + "\n")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
