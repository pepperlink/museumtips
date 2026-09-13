#!/usr/bin/env python3
"""Full-population before/after fact-diff for ST-4-2 curated-store migration.

Flattens source (legacy) and target (schema.org-shaped) records into
(record, field-path, value) tuples per PLAN.md Tables 2/2b/3 and §4.4.1.5 gate 1.
Every source tuple must map to an equal-valued target tuple; every leftover
target tuple must sit on the named constants/derived-fields allowlist.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

ACCEPTANCE = {True: "accepted", False: "not_accepted", None: "unknown"}

VARIANT_SLUGS = {
    "de-buitenplaats",
    "h-art-museum",
    "huis-marseille",
    "museum-boijmans-van-beuningen",
    "museum-volkenkunde",
    "stedelijk-museum",
    "voorlinden",
}

# Named allowlist from §4.4.1.5 gate 1, plus `_meta.generatedNameVariant`
# (Table 2 / delta F1 — derived from exhibitions.json, not a museums_info source leaf).
ALLOWLIST_PATHS = {
    "@type",
    "category",
    "addressCountry",
    "streetAddress",
    "postalCode",
    "addressLocality",
    "venueNote",
    "generatedNameVariant",
}


def git_show(commit: str, path: str) -> str:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], text=True)


def canon(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def leaf_name(path: str) -> str:
    return path.rsplit(".", 1)[-1]


def is_allowlisted(path: str, value: Any) -> bool:
    leaf = leaf_name(path)
    if leaf == "@type":
        return value in (
            "Museum",
            "Offer",
            "GeoCoordinates",
            "PostalAddress",
            "NewsArticle",
            "Organization",
        )
    if leaf == "category":
        return value == "discount-card"
    if leaf == "addressCountry":
        return value == "NL"
    if leaf in {
        "streetAddress",
        "postalCode",
        "addressLocality",
        "venueNote",
        "generatedNameVariant",
    }:
        return True
    return False


def add_fact(facts: dict[tuple[str, str], Any], slug: str, path: str, value: Any) -> None:
    key = (slug, path)
    if key in facts:
        raise SystemExit(f"duplicate fact tuple: {slug} {path}")
    facts[key] = value


def flatten_museums_source(data: dict) -> dict[tuple[str, str], Any]:
    facts: dict[tuple[str, str], Any] = {}
    for slug, rec in data.items():
        add_fact(facts, slug, "name", rec["name"])
        add_fact(facts, slug, "description.nl", rec["description_nl"])
        add_fact(facts, slug, "description.en", rec["description_en"])
        add_fact(facts, slug, "address_display", rec["address"])
        add_fact(facts, slug, "geo.latitude", rec["lat"])
        add_fact(facts, slug, "geo.longitude", rec["lon"])
        for group in ("hours", "transit", "parking", "access", "pricing"):
            for lang in ("nl", "en"):
                add_fact(facts, slug, f"_visitor.{group}.{lang}", rec[f"{group}_{lang}"])
        for i, card in enumerate(rec["cards"]):
            ident = card["id"]
            prefix = f"offers[{ident}]"
            add_fact(facts, slug, f"{prefix}.identifier", ident)
            add_fact(facts, slug, f"{prefix}.name", card["label"])
            add_fact(facts, slug, f"{prefix}.acceptance", ACCEPTANCE[card["accepted"]])
            nl = card.get("note_nl", card.get("notes_nl"))
            en = card.get("note_en", card.get("notes_en"))
            if nl is not None:
                add_fact(facts, slug, f"{prefix}.description.nl", nl)
            if en is not None:
                add_fact(facts, slug, f"{prefix}.description.en", en)
        for i, src in enumerate(rec["sources"]):
            add_fact(facts, slug, f"_meta.sources[{i}].fact", src["fact"])
            add_fact(facts, slug, f"_meta.sources[{i}].url", src["url"])
        for i, note in enumerate(rec["notes"]):
            add_fact(facts, slug, f"_meta.notes[{i}]", note)
        add_fact(facts, slug, "_meta.verified", rec["verified"])
    return facts


def flatten_museums_target(data: dict) -> dict[tuple[str, str], Any]:
    facts: dict[tuple[str, str], Any] = {}
    for slug, rec in data.items():
        add_fact(facts, slug, "@type", rec.get("@type"))
        add_fact(facts, slug, "name", rec.get("name"))
        desc = rec.get("description") or {}
        if "nl" in desc:
            add_fact(facts, slug, "description.nl", desc["nl"])
        if "en" in desc:
            add_fact(facts, slug, "description.en", desc["en"])
        add_fact(facts, slug, "address_display", rec.get("address_display"))
        addr = rec.get("address_v2") or {}
        add_fact(facts, slug, "address_v2.@type", addr.get("@type"))
        add_fact(facts, slug, "address_v2.streetAddress", addr.get("streetAddress"))
        add_fact(facts, slug, "address_v2.postalCode", addr.get("postalCode"))
        add_fact(facts, slug, "address_v2.addressLocality", addr.get("addressLocality"))
        add_fact(facts, slug, "address_v2.addressCountry", addr.get("addressCountry"))
        if "venueNote" in addr:
            add_fact(facts, slug, "address_v2.venueNote", addr.get("venueNote"))
        geo = rec.get("geo") or {}
        add_fact(facts, slug, "geo.@type", geo.get("@type"))
        add_fact(facts, slug, "geo.latitude", geo.get("latitude"))
        add_fact(facts, slug, "geo.longitude", geo.get("longitude"))
        for offer in rec.get("offers") or []:
            ident = offer.get("identifier")
            prefix = f"offers[{ident}]"
            add_fact(facts, slug, f"{prefix}.@type", offer.get("@type"))
            add_fact(facts, slug, f"{prefix}.category", offer.get("category"))
            add_fact(facts, slug, f"{prefix}.identifier", ident)
            add_fact(facts, slug, f"{prefix}.name", offer.get("name"))
            add_fact(facts, slug, f"{prefix}.acceptance", offer.get("acceptance"))
            odesc = offer.get("description") or {}
            if "nl" in odesc:
                add_fact(facts, slug, f"{prefix}.description.nl", odesc["nl"])
            if "en" in odesc:
                add_fact(facts, slug, f"{prefix}.description.en", odesc["en"])
        visitor = rec.get("_visitor") or {}
        for group in ("hours", "transit", "parking", "access", "pricing"):
            node = visitor.get(group) or {}
            for lang in ("nl", "en"):
                if lang in node:
                    add_fact(facts, slug, f"_visitor.{group}.{lang}", node[lang])
        meta = rec.get("_meta") or {}
        for i, src in enumerate(meta.get("sources") or []):
            add_fact(facts, slug, f"_meta.sources[{i}].fact", src.get("fact"))
            add_fact(facts, slug, f"_meta.sources[{i}].url", src.get("url"))
            if "checked" in src:
                add_fact(facts, slug, f"_meta.sources[{i}].checked", src.get("checked"))
        for i, note in enumerate(meta.get("notes") or []):
            add_fact(facts, slug, f"_meta.notes[{i}]", note)
        if "verified" in meta:
            add_fact(facts, slug, "_meta.verified", meta.get("verified"))
        if "generatedNameVariant" in meta:
            add_fact(facts, slug, "_meta.generatedNameVariant", meta.get("generatedNameVariant"))
    return facts


def flatten_exhibitions_source(data: dict) -> dict[tuple[str, str], Any]:
    facts: dict[tuple[str, str], Any] = {}
    for slug, rec in data.items():
        adm = rec["admission"]
        add_fact(facts, slug, "admission_v2.admissionStatus", adm["museumkaart"])
        add_fact(facts, slug, "admission_v2.description.nl", adm["note_nl"])
        add_fact(facts, slug, "admission_v2.description.en", adm["note_en"])
        add_fact(facts, slug, "_meta.admission.source", adm["source"])
        add_fact(facts, slug, "_meta.admission.verified", adm["verified"])
        for i, article in enumerate(rec.get("press") or []):
            prefix = f"subjectOf[{i}]"
            add_fact(facts, slug, f"{prefix}.headline", article["title"])
            add_fact(facts, slug, f"{prefix}.publisher.name", article["outlet"])
            add_fact(facts, slug, f"{prefix}.url", article["url"])
            add_fact(facts, slug, f"{prefix}.inLanguage", article["lang"])
            add_fact(facts, slug, f"{prefix}.datePublished", article["date"])
        add_fact(facts, slug, "_meta.verified", rec["verified"])
    return facts


def flatten_exhibitions_target(data: dict) -> dict[tuple[str, str], Any]:
    facts: dict[tuple[str, str], Any] = {}
    for slug, rec in data.items():
        if "@type" in rec:
            add_fact(facts, slug, "@type", rec["@type"])
        off = rec.get("admission_v2") or {}
        add_fact(facts, slug, "admission_v2.@type", off.get("@type"))
        add_fact(facts, slug, "admission_v2.admissionStatus", off.get("admissionStatus"))
        desc = off.get("description") or {}
        if "nl" in desc:
            add_fact(facts, slug, "admission_v2.description.nl", desc["nl"])
        if "en" in desc:
            add_fact(facts, slug, "admission_v2.description.en", desc["en"])
        for i, article in enumerate(rec.get("subjectOf") or []):
            prefix = f"subjectOf[{i}]"
            add_fact(facts, slug, f"{prefix}.@type", article.get("@type"))
            add_fact(facts, slug, f"{prefix}.headline", article.get("headline"))
            pub = article.get("publisher") or {}
            add_fact(facts, slug, f"{prefix}.publisher.@type", pub.get("@type"))
            add_fact(facts, slug, f"{prefix}.publisher.name", pub.get("name"))
            add_fact(facts, slug, f"{prefix}.url", article.get("url"))
            add_fact(facts, slug, f"{prefix}.inLanguage", article.get("inLanguage"))
            add_fact(facts, slug, f"{prefix}.datePublished", article.get("datePublished"))
            if "archiveUrl" in article:
                add_fact(facts, slug, f"{prefix}.archiveUrl", article.get("archiveUrl"))
            if "verifiedAccess" in article:
                add_fact(facts, slug, f"{prefix}.verifiedAccess", article.get("verifiedAccess"))
            if "accessNote" in article:
                add_fact(facts, slug, f"{prefix}.accessNote", article.get("accessNote"))
            if "accessChecked" in article:
                add_fact(facts, slug, f"{prefix}.accessChecked", article.get("accessChecked"))
        meta = rec.get("_meta") or {}
        adm = meta.get("admission") or {}
        if "source" in adm:
            add_fact(facts, slug, "_meta.admission.source", adm.get("source"))
        if "verified" in adm:
            add_fact(facts, slug, "_meta.admission.verified", adm.get("verified"))
        if "verified" in meta:
            add_fact(facts, slug, "_meta.verified", meta.get("verified"))
        if "orphaned_since" in meta:
            add_fact(facts, slug, "_meta.orphaned_since", meta.get("orphaned_since"))
    return facts


def diff_facts(source: dict, target: dict) -> list[str]:
    errors: list[str] = []
    for key, src_val in source.items():
        slug, path = key
        if key not in target:
            errors.append(f"unconsumed source: {slug} {path}={canon(src_val)}")
            continue
        if target[key] != src_val:
            errors.append(
                f"value mismatch: {slug} {path} source={canon(src_val)} target={canon(target[key])}"
            )
    for key, tgt_val in target.items():
        if key in source:
            continue
        slug, path = key
        if not is_allowlisted(path, tgt_val):
            errors.append(f"unexplained target: {slug} {path}={canon(tgt_val)}")
        elif tgt_val is None and leaf_name(path) not in {"postalCode", "venueNote", "archiveUrl"}:
            errors.append(f"allowlisted target is unexpectedly null: {slug} {path}")
    return errors


def check_name_variants(before_museums: dict, candidate: dict, generated: dict) -> list[str]:
    gen_names = {row["slug"]: row["name"] for row in generated["museums"]}
    errors: list[str] = []
    for slug, rec in candidate.items():
        variant = (rec.get("_meta") or {}).get("generatedNameVariant")
        curated_name = rec.get("name")
        gen_name = gen_names.get(slug)
        if slug in VARIANT_SLUGS:
            if variant != gen_name:
                errors.append(
                    f"generatedNameVariant mismatch: {slug} {canon(variant)} != {canon(gen_name)}"
                )
        else:
            if variant is not None:
                errors.append(f"unexpected generatedNameVariant on {slug}")
            if curated_name != gen_name:
                errors.append(f"name != generated name for non-variant {slug}")
        before_name = before_museums[slug]["name"]
        if curated_name != before_name:
            errors.append(f"curated name changed: {slug}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True, choices=("museums", "exhibitions"))
    parser.add_argument("--before-commit", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()

    with open(args.candidate, encoding="utf-8") as fh:
        candidate = json.load(fh)

    errors: list[str] = []
    if args.domain == "museums":
        before = json.loads(git_show(args.before_commit, "data/museums_info.json"))
        generated = json.loads(git_show(args.before_commit, "data/exhibitions.json"))
        source = flatten_museums_source(before)
        target = flatten_museums_target(candidate)
        errors.extend(diff_facts(source, target))
        errors.extend(check_name_variants(before, candidate, generated))
        if len(before) != 30 or len(candidate) != 30:
            errors.append(f"museum count {len(before)}/{len(candidate)} (expected 30/30)")
    else:
        before = json.loads(git_show(args.before_commit, "data/exhibitions_info.json"))
        source = flatten_exhibitions_source(before)
        target = flatten_exhibitions_target(candidate)
        errors.extend(diff_facts(source, target))
        if len(before) != 187 or len(candidate) != 187:
            errors.append(f"exhibition count {len(before)}/{len(candidate)} (expected 187/187)")

    if errors:
        print(f"verify-losslessness.py FAIL ({args.domain}): {len(errors)} error(s)", file=sys.stderr)
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print(
        f"verify-losslessness.py OK ({args.domain}): "
        f"{len(source)} source tuples mapped; "
        f"{len(target) - len(source)} allowlisted derived tuples"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
