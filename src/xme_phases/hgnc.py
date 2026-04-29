from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import BuildMeta

HGNC_COMPLETE_SET_TSV = "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt"


def default_cache_dir() -> Path:
    root = os.environ.get("XDG_CACHE_HOME")
    if root:
        return Path(root) / "xme_phase_list"
    return Path.home() / ".cache" / "xme_phase_list"


def download_hgnc_complete_set(
    cache_dir: str | Path | None = None,
    refresh: bool = False,
    url: str = HGNC_COMPLETE_SET_TSV,
    timeout: int = 60,
) -> tuple[Path, BuildMeta]:
    """Download HGNC complete-set TSV with conditional caching.

    HGNC publishes current data files in Google Cloud Storage. This function
    stores the TSV and a small metadata JSON file. Later calls send ETag and
    Last-Modified headers so unchanged data do not get downloaded again.
    """
    cache = Path(cache_dir) if cache_dir else default_cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / "hgnc_complete_set.txt"
    meta_path = cache / "hgnc_complete_set.meta.json"
    old_meta: dict[str, str] = {}
    if meta_path.exists():
        try:
            old_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old_meta = {}

    headers = {"User-Agent": "xme-phase-list/0.1 (+https://www.genenames.org/download/)"}
    if not refresh:
        if old_meta.get("etag"):
            headers["If-None-Match"] = old_meta["etag"]
        if old_meta.get("last_modified"):
            headers["If-Modified-Since"] = old_meta["last_modified"]

    req = Request(url, headers=headers)
    refreshed = False
    try:
        with urlopen(req, timeout=timeout) as response:
            data = response.read()
            dest.write_bytes(data)
            refreshed = True
            new_meta = {
                "url": url,
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "etag": response.headers.get("ETag", ""),
                "last_modified": response.headers.get("Last-Modified", ""),
            }
            meta_path.write_text(json.dumps(new_meta, indent=2), encoding="utf-8")
            old_meta = new_meta
    except HTTPError as exc:
        if exc.code == 304 and dest.exists():
            # Cached file is current.
            pass
        elif dest.exists() and not refresh:
            # Fallback to last cached copy if the server is temporarily unavailable.
            pass
        else:
            raise RuntimeError(f"Unable to download HGNC data from {url}: HTTP {exc.code}") from exc
    except URLError as exc:
        if dest.exists() and not refresh:
            pass
        else:
            raise RuntimeError(f"Unable to download HGNC data from {url}: {exc}") from exc

    if not dest.exists():
        raise RuntimeError("HGNC cache file is missing after download attempt.")

    meta = BuildMeta(
        source_url=url,
        downloaded_at=old_meta.get("downloaded_at", datetime.now(timezone.utc).isoformat()),
        cache_path=str(dest),
        refreshed=refreshed,
        hgnc_last_modified=old_meta.get("last_modified", ""),
        hgnc_etag=old_meta.get("etag", ""),
    )
    return dest, meta


def read_hgnc_tsv(path: str | Path) -> list[dict[str, str]]:
    """Read HGNC TSV rows as dictionaries."""
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [{k: (v or "") for k, v in row.items()} for row in reader]


def split_pipe(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split("|") if part.strip()]
