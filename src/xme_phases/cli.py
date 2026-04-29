from __future__ import annotations

import argparse
import json
from pathlib import Path

from .builder import build_xme_list, summarize, write_table
from .references import REFERENCES, references_as_bibtex


def _cmd_build(args: argparse.Namespace) -> int:
    records = build_xme_list(
        tier=args.tier,
        cache_dir=args.cache_dir,
        refresh=args.refresh,
        hgnc_tsv_path=args.hgnc_tsv,
        protein_coding_only=not args.include_non_coding,
    )
    out = write_table(records, args.out, fmt=args.format)
    print(json.dumps({"output": str(out), **summarize(records)}, indent=2))
    return 0


def _cmd_refs(args: argparse.Namespace) -> int:
    out = Path(args.out) if args.out else None
    if args.format == "bibtex":
        text = references_as_bibtex()
    else:
        text = json.dumps(REFERENCES, indent=2, ensure_ascii=False) + "\n"
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(str(out))
    else:
        print(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="xme-phase-list",
        description="Build curated Phase I, Phase II, and Phase III xenobiotic metabolism gene lists from HGNC.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Download HGNC and build the XME phase list")
    build.add_argument("--tier", choices=["core", "extended"], default="core", help="core = concise review list; extended = broader family list")
    build.add_argument("--out", default="xme_phase_list.csv", help="Output path")
    build.add_argument("--format", choices=["csv", "tsv", "json"], default=None, help="Output format; inferred from extension if omitted")
    build.add_argument("--cache-dir", default=None, help="Cache directory for HGNC download")
    build.add_argument("--refresh", action="store_true", help="Force redownload of HGNC data")
    build.add_argument("--hgnc-tsv", default=None, help="Use a local HGNC complete-set TSV instead of downloading")
    build.add_argument("--include-non-coding", action="store_true", help="Do not filter out non-protein-coding HGNC loci")
    build.set_defaults(func=_cmd_build)

    refs = sub.add_parser("refs", help="Print or save source references")
    refs.add_argument("--format", choices=["json", "bibtex"], default="bibtex")
    refs.add_argument("--out", default=None, help="Output path; prints to stdout if omitted")
    refs.set_defaults(func=_cmd_refs)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
