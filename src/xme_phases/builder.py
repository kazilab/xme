from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Sequence

from .hgnc import download_hgnc_complete_set, read_hgnc_tsv
from .models import GeneRecord, Rule
from .references import REFERENCES
from .rules import RULES

FIELDNAMES = [
    "symbol", "name", "hgnc_id", "phase", "family", "role", "tier",
    "reference_ids", "references", "hgnc_url", "entrez_id", "ensembl_gene_id",
    "uniprot_ids", "location", "locus_group", "locus_type", "gene_group", "gene_group_id", "rule_note",
    "source_url", "source_downloaded_at",
]

TIER_ORDER = {"core": 0, "extended": 1}


def _rule_allowed(rule: Rule, tier: str) -> bool:
    requested = TIER_ORDER.get(tier, 0)
    return TIER_ORDER.get(rule.tier, 99) <= requested


def _best_rule_for_gene(row: dict[str, str], rules: Sequence[Rule], tier: str) -> Rule | None:
    matches = [r for r in rules if _rule_allowed(r, tier) and r.matches(row)]
    if not matches:
        return None
    # Prefer core over extended and earlier, more specific rules over later broad rules.
    return sorted(matches, key=lambda r: (TIER_ORDER.get(r.tier, 99), rules.index(r)))[0]


def _compact_reference(ref_id: str) -> str:
    ref = REFERENCES.get(ref_id)
    if not ref:
        return ref_id
    doi = f" doi:{ref['doi']}" if ref.get("doi") else ""
    return f"{ref['label']} ({ref['url']};{doi})"


def build_xme_list(
    tier: str = "core",
    cache_dir: str | Path | None = None,
    refresh: bool = False,
    hgnc_tsv_path: str | Path | None = None,
    rules: Sequence[Rule] = RULES,
    protein_coding_only: bool = True,
) -> list[GeneRecord]:
    """Build the curated Phase I/II/III XME gene list.

    Parameters
    ----------
    tier:
        "core" gives a review-paper sized list. "extended" adds broader CYP,
        ABC, and SLC/SLCO family members.
    cache_dir:
        Directory for cached HGNC data.
    refresh:
        Force redownload of HGNC data instead of conditional caching.
    hgnc_tsv_path:
        Optional local HGNC TSV for offline/reproducible builds.
    rules:
        Override curation rules, useful for project-specific lists.
    protein_coding_only:
        Exclude pseudogenes and other non-protein-coding loci when HGNC locus_group is available.
    """
    if tier not in TIER_ORDER:
        raise ValueError("tier must be 'core' or 'extended'")

    if hgnc_tsv_path:
        rows = read_hgnc_tsv(hgnc_tsv_path)
        source_url = str(hgnc_tsv_path)
        downloaded_at = "local-file"
    else:
        path, meta = download_hgnc_complete_set(cache_dir=cache_dir, refresh=refresh)
        rows = read_hgnc_tsv(path)
        source_url = meta.source_url
        downloaded_at = meta.downloaded_at

    records: list[GeneRecord] = []
    for row in rows:
        status = row.get("status", "Approved") or "Approved"
        if status.lower() != "approved":
            continue
        locus_group = row.get("locus_group", "").strip().lower()
        if protein_coding_only and locus_group and locus_group != "protein-coding gene":
            continue
        rule = _best_rule_for_gene(row, rules, tier=tier)
        if not rule:
            continue
        symbol = row.get("symbol", "").strip()
        hgnc_id = row.get("hgnc_id", "").strip()
        hgnc_url = f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{hgnc_id}" if hgnc_id else ""
        records.append(
            GeneRecord(
                symbol=symbol,
                name=row.get("name", ""),
                hgnc_id=hgnc_id,
                phase=rule.phase,
                family=rule.family,
                role=rule.role,
                tier=rule.tier,
                reference_ids=list(rule.references),
                references=[_compact_reference(ref_id) for ref_id in rule.references],
                hgnc_url=hgnc_url,
                entrez_id=row.get("entrez_id", ""),
                ensembl_gene_id=row.get("ensembl_gene_id", ""),
                uniprot_ids=row.get("uniprot_ids", ""),
                location=row.get("location", ""),
                locus_group=row.get("locus_group", ""),
                locus_type=row.get("locus_type", ""),
                gene_group=row.get("gene_group", ""),
                gene_group_id=row.get("gene_group_id", ""),
                rule_note=rule.note,
                source_url=source_url,
                source_downloaded_at=downloaded_at,
            )
        )

    # Stable sort: phase order, family, symbol.
    phase_order = {"Phase I": 1, "Phase II": 2, "Phase III": 3}
    records.sort(key=lambda r: (phase_order.get(r.phase, 99), r.family, r.symbol))
    return records


def write_table(records: Sequence[GeneRecord], out: str | Path, fmt: str | None = None) -> Path:
    """Write records to CSV, TSV, or JSON."""
    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    fmt = (fmt or output.suffix.lstrip(".") or "csv").lower()
    rows = [record.to_row() for record in records]

    if fmt == "json":
        output.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    elif fmt in {"csv", "tsv"}:
        delimiter = "\t" if fmt == "tsv" else ","
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise ValueError("fmt must be one of: csv, tsv, json")
    return output


def summarize(records: Sequence[GeneRecord]) -> dict[str, object]:
    by_phase: dict[str, int] = {}
    by_family: dict[str, int] = {}
    for record in records:
        by_phase[record.phase] = by_phase.get(record.phase, 0) + 1
        by_family[record.family] = by_family.get(record.family, 0) + 1
    return {"n_genes": len(records), "by_phase": by_phase, "by_family": by_family}
