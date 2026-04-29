# Xenobiotic-Metabolizing Enzymes (XME) Explorer

<!-- PyPI version badge -->
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://xme.streamlit.app)
<!--[![PyPI version](https://img.shields.io/pypi/v/ExposoGraph.svg)](https://pypi.org/project/ExposoGraph/)-->
<!--[![Documentation Status](https://readthedocs.org/projects/ExposoGraph/badge/?version=latest)](https://ExposoGraph.readthedocs.io/en/latest/?badge=latest)-->
<!--[![ResearchSquare](https://img.shields.io/badge/ResearchSquare-rs--9202489%2Fv1-00A0E0.svg)](https://www.researchsquare.com/article/rs-9202489/v1)-->
<!--[![bioRxiv](https://img.shields.io/badge/bioRxiv-10.64898%2F2026.03.22.713456-b31b1b.svg)](https://doi.org/10.64898/2026.03.22.713456)-->
<!-- PyPI version badge -->
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-kazilab%2Fcarcinogen_harmonizer-181717?logo=github&logoColor=white)](https://github.com/kazilab/carcinogen_harmonizer)
[![@KaziLab.se](https://img.shields.io/website?url=https://www.kazilab.se/)](https://www.kazilab.se/)
<!-- PyPI version badge -->

`xme-phase-list` builds a curated, reference-backed list of human xenobiotic-metabolizing enzymes and transporters grouped by:

- **Phase I**: functionalization, oxidation, reduction, hydrolysis, monoamine oxidation, and key CYP modifiers
- **Phase II**: conjugation, electrophile scavenging, amino acid conjugation, and quinone/catechol detoxication
- **Phase III**: ABC efflux and SLC/SLCO uptake or bidirectional transport

The package downloads the current HGNC complete gene set, validates current approved human gene symbols, applies a curated phase/family mapping, and exports CSV/TSV/JSON with source references.

## Why this design?

HGNC is the best source for current approved human gene symbols, but it does **not** define ADME Phase I/II/III categories. This package therefore separates:

1. **Live nomenclature data** from HGNC.
2. **Curated phase/family rules** in `xme_phases.rules`.
3. **Reference metadata** for the data sources used to justify the list.

## Install locally

```bash
python -m pip install -e .
```

No mandatory third-party dependencies are required.

## Streamlit app

Install the app dependencies and run the interactive explorer:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app lets you build the core or extended XME list, filter by phase, family, reference source, and keyword, inspect source references, and download filtered or full CSV/JSON/BibTeX files.

For Streamlit Community Cloud, use:

- Repository: this project
- Branch: `main`
- Main file path: `app.py`
- Python dependencies: `requirements.txt`

## CLI usage

Build a concise core list:

```bash
xme-phase-list build --tier core --out xme_phase_core.csv
```

Build a broader list including all approved human CYPs, selected broad ABC families, and broad ADME-relevant SLC/SLCO families:

```bash
xme-phase-list build --tier extended --out xme_phase_extended.csv
```

Export as JSON:

```bash
xme-phase-list build --tier core --format json --out xme_phase_core.json
```

Force a fresh HGNC download:

```bash
xme-phase-list build --refresh --out xme_phase_core.csv
```

Use a reproducible local HGNC file:

```bash
xme-phase-list build --hgnc-tsv data/hgnc_complete_set.txt --out xme_phase_core.csv
```

Export references as BibTeX:

```bash
xme-phase-list refs --format bibtex --out xme_phase_refs.bib
```

## Python usage

```python
from xme_phases import build_xme_list, write_table

records = build_xme_list(tier="core")
write_table(records, "xme_phase_core.csv")
```

## Notebook

Open `notebooks/run_xme_phases.ipynb` to build core and extended lists, preview phase/family summaries, check MAO and amino acid conjugation coverage, and export CSV/JSON/BibTeX files to `outputs/`.

## Output columns

- `symbol`, `name`, `hgnc_id`
- `phase`, `family`, `role`, `tier`
- `reference_ids`, `references`
- `hgnc_url`, `entrez_id`, `ensembl_gene_id`, `uniprot_ids`
- `location`, `locus_group`, `locus_type`, `gene_group`, `gene_group_id`
- `rule_note`, `source_url`, `source_downloaded_at`

## Source references included

The package includes BibTeX/JSON metadata for:

- HGNC gene nomenclature and current downloads
- XMetDB xenobiotic biotransformation evidence
- BRENDA enzyme functional and reaction data
- ClinPGx/PharmGKB pharmacogenomic annotations
- PharmVar star-allele nomenclature
- FDA drug interaction tables for CYP enzymes and transporters
- TCDB transporter classification
- ISTransbase transporter inhibitor/substrate evidence
- SLC Tables solute-carrier family and member curation

## Curation notes

By default the package filters to HGNC protein-coding genes when the `locus_group` column is available; pass `--include-non-coding` to keep pseudogenes and other loci.

The default **core** list is meant for a review article on human enzymes in carcinogen metabolism. It intentionally includes the best-known ADME/carcinogen genes rather than every possible oxidoreductase, transferase, or transporter. The **extended** tier is useful for discovery work but should be manually narrowed before publication.

The core list includes monoamine oxidases and amino acid conjugation enzymes in addition to CYP, non-CYP Phase I, conjugation, quinone-reduction, ABC, and SLC/SLCO families.

To modify the list, edit `src/xme_phases/rules.py` or pass a custom `rules` sequence into `build_xme_list()`.

## GitHub upload checklist

```bash
git init
git add .
git commit -m "Add XME phase list Streamlit app"
git branch -M main
git remote add origin https://github.com/julhashkazi/xme-phase-list.git
git push -u origin main
```

The repository includes `.gitignore`, `requirements.txt`, `.streamlit/config.toml`, and a GitHub Actions workflow that installs the app extras, runs tests, and compiles `app.py`.

## Limitations

- HGNC provides current gene identities; phase labels are curated by this package.
- XMetDB and transporter databases are evidence resources, not complete classifiers for every carcinogen.
- Phase boundaries are simplified. Some enzymes can detoxify one substrate and activate another.
- Always cite the underlying primary literature for substrate-specific claims in a manuscript.
