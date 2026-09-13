#!/usr/bin/env python3
"""Curated-record reconciliation for museumtips phase 4 (ST-4-6a).

Repeatable cadence-cycle script: add schema-valid stubs for generated slugs
missing curated records; assign museum refresh_group via smaller-group-wins;
apply exhibition orphan grace via completed A+B cadence markers (not wall-clock).
"""
from __future__ import annotations

import argparse
import copy
import datetime
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
EXHIBITIONS_JSON = ROOT / "data" / "exhibitions.json"
MUSEUMS_INFO = ROOT / "data" / "museums_info.json"
EXHIBITIONS_INFO = ROOT / "data" / "exhibitions_info.json"

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


def exhibition_stub() -> dict[str, Any]:
    """Schema-valid exhibition stub per PLAN.md §4.4.2 item 1."""
    return {
        "admission_v2": {
            "@type": "Offer",
            "admissionStatus": "unknown",
            "description": {"nl": "", "en": ""},
        },
        "subjectOf": [],
        "_meta": {
            "verified": None,
            "orphaned_since": None,
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


def both_groups_completed_since(
    orphaned_since: str, cadence: dict[str, Any]
) -> bool:
    last_a = cadence.get("last_completed_a") or ""
    last_b = cadence.get("last_completed_b") or ""
    return last_a > orphaned_since and last_b > orphaned_since


def reconcile_exhibitions(
    exhibitions: dict[str, Any],
    generated: dict[str, Any],
    cadence: dict[str, Any],
    run_date: str,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Return updated exhibitions dict and action counts."""
    gen_slugs = {row["slug"] for row in generated["exhibitions"]}
    out = copy.deepcopy(exhibitions)
    counts = {
        "stubs_added": 0,
        "orphaned_stamped": 0,
        "orphaned_cleared": 0,
        "orphans_deleted": 0,
        "retained_orphans": 0,
    }

    for slug in sorted(gen_slugs - set(out)):
        out[slug] = exhibition_stub()
        counts["stubs_added"] += 1

    for slug in sorted(list(out.keys())):
        record = out[slug]
        meta = record.setdefault("_meta", {})
        in_generated = slug in gen_slugs

        if in_generated:
            if meta.get("orphaned_since"):
                meta["orphaned_since"] = None
                counts["orphaned_cleared"] += 1
            continue

        orphaned_since = meta.get("orphaned_since")
        if not orphaned_since:
            meta["orphaned_since"] = run_date
            counts["orphaned_stamped"] += 1
            counts["retained_orphans"] += 1
            continue

        if both_groups_completed_since(orphaned_since, cadence):
            del out[slug]
            counts["orphans_deleted"] += 1
        else:
            counts["retained_orphans"] += 1

    return out, counts


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


def run_exhibitions_domain(run_date: str | None = None) -> None:
    if run_date is None:
        run_date = datetime.date.today().isoformat()
    generated = load_json(EXHIBITIONS_JSON)
    museums = load_json(MUSEUMS_INFO)
    exhibitions = load_json(EXHIBITIONS_INFO)
    cadence = museums["_cadence"]
    updated, counts = reconcile_exhibitions(exhibitions, generated, cadence, run_date)
    save_json(EXHIBITIONS_INFO, updated)
    print(
        "exhibitions reconciliation:",
        f"{counts['stubs_added']} stub(s) added;",
        f"{counts['orphaned_stamped']} newly orphaned;",
        f"{counts['orphaned_cleared']} reappeared;",
        f"{counts['orphans_deleted']} expired orphan(s) deleted;",
        f"{counts['retained_orphans']} retained orphan(s)",
    )


def run_fixture_tests() -> None:
    """Four named reconciliation fixtures (PLAN.md ST-4-6a, delta F15)."""
    run_date = "2026-09-13"

    # first-seen: generated slug, no curated record → stub, not orphaned
    gen = {
        "museums": [{"slug": "new-museum", "name": "New Museum"}],
        "exhibitions": [{"slug": "new-show"}],
    }
    museums_in: dict[str, Any] = {
        "_cadence": {"last_completed_a": None, "last_completed_b": None}
    }
    museums_out, stub_count = reconcile_museums(museums_in, gen)
    assert stub_count == 1, stub_count
    assert "new-museum" in museums_out
    assert museums_out["new-museum"]["refresh_group"] in ("A", "B")
    ex_in: dict[str, Any] = {}
    ex_out, ex_counts = reconcile_exhibitions(
        ex_in, gen, museums_in["_cadence"], run_date
    )
    assert ex_counts["stubs_added"] == 1
    assert ex_out["new-show"]["_meta"]["orphaned_since"] is None

    # retained: absent, orphaned_since set, cadence incomplete → untouched
    gen_ret = {"museums": [], "exhibitions": []}
    cadence_open = {"last_completed_a": None, "last_completed_b": None}
    ex_ret = {
        "gone-show": {
            "admission_v2": {
                "@type": "Offer",
                "admissionStatus": "unknown",
                "description": {"nl": "", "en": ""},
            },
            "subjectOf": [],
            "_meta": {"verified": None, "orphaned_since": "2026-09-01"},
        }
    }
    before_stamp = ex_ret["gone-show"]["_meta"]["orphaned_since"]
    ex_ret_out, ex_ret_counts = reconcile_exhibitions(
        ex_ret, gen_ret, cadence_open, run_date
    )
    assert "gone-show" in ex_ret_out
    assert ex_ret_out["gone-show"]["_meta"]["orphaned_since"] == before_stamp
    assert ex_ret_counts["orphans_deleted"] == 0

    # reappeared: slug back in generated → orphaned_since cleared
    gen_back = {"museums": [], "exhibitions": [{"slug": "back-show"}]}
    ex_reap = {
        "back-show": {
            "admission_v2": {
                "@type": "Offer",
                "admissionStatus": "included",
                "description": {"nl": "", "en": ""},
            },
            "subjectOf": [],
            "_meta": {"verified": "2026-09-12", "orphaned_since": "2026-09-01"},
        }
    }
    ex_reap_out, ex_reap_counts = reconcile_exhibitions(
        ex_reap, gen_back, cadence_open, run_date
    )
    assert ex_reap_out["back-show"]["_meta"]["orphaned_since"] is None
    assert ex_reap_counts["orphaned_cleared"] == 1

    # expired-orphan: both cadence markers postdate orphaned_since → deleted
    cadence_done = {"last_completed_a": "2026-09-10", "last_completed_b": "2026-09-12"}
    ex_exp = {
        "old-show": {
            "admission_v2": {
                "@type": "Offer",
                "admissionStatus": "unknown",
                "description": {"nl": "", "en": ""},
            },
            "subjectOf": [],
            "_meta": {"verified": None, "orphaned_since": "2026-09-01"},
        }
    }
    ex_exp_out, ex_exp_counts = reconcile_exhibitions(
        ex_exp, gen_ret, cadence_done, run_date
    )
    assert "old-show" not in ex_exp_out
    assert ex_exp_counts["orphans_deleted"] == 1

    print("reconcile-curated fixture tests: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domain",
        choices=("museums", "exhibitions"),
        help="Curated domain to reconcile",
    )
    parser.add_argument(
        "--test-fixtures",
        action="store_true",
        help="Run the four named reconciliation fixture tests and exit",
    )
    args = parser.parse_args()

    if args.test_fixtures:
        run_fixture_tests()
        return

    if args.domain is None:
        parser.error("--domain is required unless --test-fixtures is set")

    if args.domain == "museums":
        run_museums_domain()
    elif args.domain == "exhibitions":
        run_exhibitions_domain()
    else:
        raise SystemExit(f"unsupported domain: {args.domain}")


if __name__ == "__main__":
    main()
