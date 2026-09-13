#!/usr/bin/env python3
"""Curated-record reconciliation for museumtips phase 4 (ST-4-6a).

Repeatable cadence-cycle script: add schema-valid stubs for generated slugs
missing curated records; assign museum refresh_group via smaller-group-wins.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
EXHIBITIONS_JSON = ROOT / "data" / "exhibitions.json"
MUSEUMS_INFO = ROOT / "data" / "museums_info.json"

UNKNOWN = "unknown"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def museum_stub(slug: str, generated_name: str, refresh_group: str) -> dict[str, Any]:
    """Schema-valid museum stub per PLAN.md §4.4.2 item 1."""
    return {
        "@type": "Museum",
        "name": generated_name,
        "description": {"nl": UNKNOWN, "en": UNKNOWN},
        "address_display": None,
        "address_v2": {
            "@type": "PostalAddress",
            "streetAddress": None,
            "postalCode": None,
            "addressLocality": None,
            "addressCountry": "NL",
            "venueNote": None,
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": None,
            "longitude": None,
        },
        "offers": [],
        "_visitor": {
            "hours": {"nl": UNKNOWN, "en": UNKNOWN},
            "transit": {"nl": UNKNOWN, "en": UNKNOWN},
            "parking": {"nl": UNKNOWN, "en": UNKNOWN},
            "access": {"nl": UNKNOWN, "en": UNKNOWN},
            "pricing": {"nl": UNKNOWN, "en": UNKNOWN},
        },
        "refresh_group": refresh_group,
        "last_refreshed_extras": None,
        "next_due": None,
        "_meta": {
            "sources": [],
            "notes": [],
            "verified": None,
        },
    }


def count_refresh_groups(museums: dict[str, Any]) -> dict[str, int]:
    groups: dict[str, int] = {}
    for key, record in museums.items():
        if key == "_cadence":
            continue
        group = record["refresh_group"]
        groups[group] = groups.get(group, 0) + 1
    return groups


def assign_refresh_group(groups: dict[str, int]) -> str:
    """Smaller-group-wins; ties broken alphabetically (group A wins)."""
    count_a = groups.get("A", 0)
    count_b = groups.get("B", 0)
    if count_a < count_b:
        return "A"
    if count_b < count_a:
        return "B"
    return "A"


def assert_group_balance(groups: dict[str, int]) -> None:
    if abs(groups.get("A", 0) - groups.get("B", 0)) > 1:
        raise SystemExit(f"refresh_group balance violated: {groups}")


def reconcile_museums(
    museums: dict[str, Any],
    generated: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    """Return updated museums dict and count of stubs added."""
    gen_by_slug = {row["slug"]: row for row in generated["museums"]}
    gen_slugs = set(gen_by_slug)
    cadence = museums.get("_cadence", {"last_completed_a": None, "last_completed_b": None})
    records = {k: v for k, v in museums.items() if k != "_cadence"}

    stubs_added = 0
    for slug in sorted(gen_slugs - set(records)):
        group = assign_refresh_group(count_refresh_groups(records))
        records[slug] = museum_stub(slug, gen_by_slug[slug]["name"], group)
        stubs_added += 1

    groups = count_refresh_groups(records)
    assert_group_balance(groups)

    out = dict(records)
    out["_cadence"] = cadence
    return out, stubs_added


def run_museums_domain() -> None:
    generated = load_json(EXHIBITIONS_JSON)
    museums = load_json(MUSEUMS_INFO)
    updated, stubs_added = reconcile_museums(museums, generated)
    if stubs_added or updated != museums:
        save_json(MUSEUMS_INFO, updated)
    groups = count_refresh_groups(updated)
    print(
        f"museums reconciliation: {stubs_added} stub(s) added; "
        f"groups {groups}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domain",
        choices=("museums",),
        required=True,
        help="Curated domain to reconcile",
    )
    args = parser.parse_args()

    if args.domain == "museums":
        run_museums_domain()
    else:
        raise SystemExit(f"unsupported domain: {args.domain}")


if __name__ == "__main__":
    main()
