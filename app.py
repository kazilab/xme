from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from xme_phases import REFERENCES, build_xme_list, references_as_bibtex  # noqa: E402


APP_CACHE_DIR = ROOT / ".cache" / "streamlit_hgnc"
OUTPUT_DIR = ROOT / "outputs"
PHASE_ORDER = ["Phase I", "Phase II", "Phase III"]
PRIMARY_COLUMNS = [
    "symbol",
    "name",
    "phase",
    "family",
    "role",
    "tier",
    "reference_ids",
    "hgnc_url",
]


def _fallback_rows(tier: str) -> list[dict[str, str]]:
    fallback = OUTPUT_DIR / f"xme_phase_{tier}.csv"
    if not fallback.exists():
        return []
    with fallback.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@st.cache_data(show_spinner=False)
def load_rows(
    tier: str,
    protein_coding_only: bool,
    refresh: bool,
    uploaded_hgnc_tsv: bytes | None,
) -> tuple[list[dict[str, str]], str, str]:
    try:
        if uploaded_hgnc_tsv:
            with tempfile.TemporaryDirectory() as tmpdir:
                hgnc_path = Path(tmpdir) / "hgnc_complete_set.txt"
                hgnc_path.write_bytes(uploaded_hgnc_tsv)
                records = build_xme_list(
                    tier=tier,
                    hgnc_tsv_path=hgnc_path,
                    protein_coding_only=protein_coding_only,
                )
        else:
            records = build_xme_list(
                tier=tier,
                cache_dir=APP_CACHE_DIR,
                refresh=refresh,
                protein_coding_only=protein_coding_only,
            )
        rows = [record.to_row() for record in records]
        source = rows[0].get("source_url", "HGNC") if rows else "HGNC"
        return rows, source, ""
    except Exception as exc:
        if uploaded_hgnc_tsv:
            raise
        rows = _fallback_rows(tier)
        if rows:
            source = str(OUTPUT_DIR / f"xme_phase_{tier}.csv")
            warning = f"Live HGNC build failed, so the bundled {tier} output is shown. Details: {exc}"
            return rows, source, warning
        raise


def reference_dataframe() -> pd.DataFrame:
    rows = [
        {
            "id": ref_id,
            "label": ref["label"],
            "doi": ref.get("doi", ""),
            "url": ref["url"],
            "citation": ref["citation"],
        }
        for ref_id, ref in REFERENCES.items()
    ]
    return pd.DataFrame(rows).sort_values("id")


def filter_dataframe(
    df: pd.DataFrame,
    query: str,
    phases: list[str],
    families: list[str],
    reference_ids: list[str],
) -> pd.DataFrame:
    filtered = df.copy()
    if phases:
        filtered = filtered[filtered["phase"].isin(phases)]
    else:
        filtered = filtered.iloc[0:0]
    if families:
        filtered = filtered[filtered["family"].isin(families)]
    else:
        filtered = filtered.iloc[0:0]
    if reference_ids:
        filtered = filtered[
            filtered["reference_ids"].fillna("").apply(
                lambda value: any(ref_id in value.split(";") for ref_id in reference_ids)
            )
        ]
    if query:
        searchable = (
            filtered[["symbol", "name", "family", "role", "reference_ids", "hgnc_id"]]
            .fillna("")
            .agg(" ".join, axis=1)
            .str.lower()
        )
        filtered = filtered[searchable.str.contains(query.lower(), regex=False)]
    return filtered


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def json_bytes(df: pd.DataFrame) -> bytes:
    return json.dumps(df.to_dict(orient="records"), indent=2, ensure_ascii=False).encode("utf-8")


def main() -> None:
    st.set_page_config(page_title="XME Phase List Explorer", layout="wide")

    with st.sidebar:
        st.header("Build")
        tier = st.radio(
            "Tier",
            options=["core", "extended"],
            format_func=lambda value: "Core" if value == "core" else "Extended",
            horizontal=True,
        )
        protein_coding_only = st.toggle("Protein-coding genes only", value=True)
        uploaded = st.file_uploader("HGNC complete-set TSV", type=["txt", "tsv"])
        refresh = st.button("Refresh HGNC", disabled=uploaded is not None, width="stretch")
        if st.button("Clear app cache", width="stretch"):
            st.cache_data.clear()
            st.rerun()

        st.divider()
        st.caption("Source rules are curated in `src/xme_phases/rules.py`.")

    uploaded_bytes = uploaded.getvalue() if uploaded else None
    with st.spinner("Building the XME phase list"):
        try:
            rows, source, warning = load_rows(tier, protein_coding_only, refresh, uploaded_bytes)
        except Exception as exc:
            st.error(f"Unable to build the XME phase list: {exc}")
            st.stop()

    if warning:
        st.warning(warning)

    df = pd.DataFrame(rows)
    if df.empty:
        st.warning("No records matched the current build settings.")
        st.stop()

    downloaded_at = df["source_downloaded_at"].dropna().iloc[0] if "source_downloaded_at" in df else ""

    st.title("XME Phase List Explorer")
    st.caption(
        "HGNC-backed Phase I, Phase II, and Phase III xenobiotic-metabolizing enzymes "
        f"and transporters. Source: {source}. Downloaded: {downloaded_at or 'not available'}."
    )

    query = st.text_input("Search symbols, names, families, roles, or references")

    phases = st.multiselect(
        "Phase",
        options=[phase for phase in PHASE_ORDER if phase in set(df["phase"])],
        default=[phase for phase in PHASE_ORDER if phase in set(df["phase"])],
    )
    families = st.multiselect(
        "Family",
        options=sorted(df["family"].dropna().unique()),
        default=sorted(df["family"].dropna().unique()),
    )
    all_reference_ids = sorted({ref for value in df["reference_ids"].dropna() for ref in value.split(";") if ref})
    reference_ids = st.multiselect("Reference source", options=all_reference_ids)

    filtered = filter_dataframe(df, query, phases, families, reference_ids)

    metric_cols = st.columns(5)
    metric_cols[0].metric("Shown genes", f"{len(filtered):,}")
    metric_cols[1].metric("Total genes", f"{len(df):,}")
    metric_cols[2].metric("Phase I", f"{int((filtered['phase'] == 'Phase I').sum()):,}")
    metric_cols[3].metric("Phase II", f"{int((filtered['phase'] == 'Phase II').sum()):,}")
    metric_cols[4].metric("Phase III", f"{int((filtered['phase'] == 'Phase III').sum()):,}")

    explorer_tab, summaries_tab, references_tab, downloads_tab = st.tabs(
        ["Explorer", "Summaries", "References", "Downloads"]
    )

    with explorer_tab:
        display_columns = [column for column in PRIMARY_COLUMNS if column in filtered.columns]
        st.dataframe(
            filtered[display_columns],
            hide_index=True,
            width="stretch",
            column_config={
                "hgnc_url": st.column_config.LinkColumn("HGNC"),
                "reference_ids": st.column_config.TextColumn("References"),
            },
        )
        with st.expander("All columns"):
            st.dataframe(filtered, hide_index=True, width="stretch")

    with summaries_tab:
        chart_cols = st.columns([1, 2])
        phase_counts = (
            filtered["phase"]
            .value_counts()
            .reindex([phase for phase in PHASE_ORDER if phase in set(filtered["phase"])])
            .dropna()
            .rename_axis("phase")
            .reset_index(name="genes")
        )
        family_counts = (
            filtered.groupby(["phase", "family"], dropna=False)
            .size()
            .reset_index(name="genes")
            .sort_values(["genes", "phase", "family"], ascending=[False, True, True])
        )
        with chart_cols[0]:
            st.subheader("By phase")
            st.bar_chart(phase_counts, x="phase", y="genes", width="stretch")
        with chart_cols[1]:
            st.subheader("Top families")
            st.bar_chart(family_counts.head(20), x="family", y="genes", width="stretch")
        st.dataframe(family_counts, hide_index=True, width="stretch")

    with references_tab:
        refs_df = reference_dataframe()
        st.dataframe(
            refs_df,
            hide_index=True,
            width="stretch",
            column_config={"url": st.column_config.LinkColumn("URL")},
        )

    with downloads_tab:
        full_name = f"xme_phase_{tier}"
        filtered_name = f"{full_name}_filtered"
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Current filters")
            st.download_button(
                "Download filtered CSV",
                data=csv_bytes(filtered),
                file_name=f"{filtered_name}.csv",
                mime="text/csv",
                width="stretch",
            )
            st.download_button(
                "Download filtered JSON",
                data=json_bytes(filtered),
                file_name=f"{filtered_name}.json",
                mime="application/json",
                width="stretch",
            )
        with col_b:
            st.subheader("Full build")
            st.download_button(
                "Download full CSV",
                data=csv_bytes(df),
                file_name=f"{full_name}.csv",
                mime="text/csv",
                width="stretch",
            )
            st.download_button(
                "Download full JSON",
                data=json_bytes(df),
                file_name=f"{full_name}.json",
                mime="application/json",
                width="stretch",
            )
            st.download_button(
                "Download BibTeX references",
                data=references_as_bibtex().encode("utf-8"),
                file_name="xme_phase_refs.bib",
                mime="application/x-bibtex",
                width="stretch",
            )


if __name__ == "__main__":
    main()
