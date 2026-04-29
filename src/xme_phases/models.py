from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping
import re


@dataclass(frozen=True)
class Rule:
    """A curated rule mapping HGNC genes to a metabolism phase/family."""

    phase: str
    family: str
    role: str
    tier: str = "core"
    symbols: tuple[str, ...] = ()
    prefixes: tuple[str, ...] = ()
    regexes: tuple[str, ...] = ()
    references: tuple[str, ...] = ("HGNC",)
    note: str = ""

    def matches(self, gene: Mapping[str, str]) -> bool:
        symbol = gene.get("symbol", "").strip().upper()
        if not symbol:
            return False
        if symbol in {s.upper() for s in self.symbols}:
            return True
        if any(symbol.startswith(p.upper()) for p in self.prefixes):
            return True
        return any(re.match(pattern, symbol, flags=re.IGNORECASE) for pattern in self.regexes)


@dataclass
class BuildMeta:
    source_url: str
    downloaded_at: str
    cache_path: str
    refreshed: bool
    hgnc_last_modified: str = ""
    hgnc_etag: str = ""


@dataclass
class GeneRecord:
    symbol: str
    name: str
    hgnc_id: str
    phase: str
    family: str
    role: str
    tier: str
    reference_ids: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    hgnc_url: str = ""
    entrez_id: str = ""
    ensembl_gene_id: str = ""
    uniprot_ids: str = ""
    location: str = ""
    locus_group: str = ""
    locus_type: str = ""
    gene_group: str = ""
    gene_group_id: str = ""
    rule_note: str = ""
    source_url: str = ""
    source_downloaded_at: str = ""

    def to_row(self) -> dict[str, str]:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "hgnc_id": self.hgnc_id,
            "phase": self.phase,
            "family": self.family,
            "role": self.role,
            "tier": self.tier,
            "reference_ids": ";".join(self.reference_ids),
            "references": " | ".join(self.references),
            "hgnc_url": self.hgnc_url,
            "entrez_id": self.entrez_id,
            "ensembl_gene_id": self.ensembl_gene_id,
            "uniprot_ids": self.uniprot_ids,
            "location": self.location,
            "locus_group": self.locus_group,
            "locus_type": self.locus_type,
            "gene_group": self.gene_group,
            "gene_group_id": self.gene_group_id,
            "rule_note": self.rule_note,
            "source_url": self.source_url,
            "source_downloaded_at": self.source_downloaded_at,
        }
