"""Tools to build curated Phase I/II/III xenobiotic metabolism gene lists."""

from .builder import build_xme_list, write_table
from .references import REFERENCES, references_as_bibtex

__all__ = ["build_xme_list", "write_table", "REFERENCES", "references_as_bibtex"]
__version__ = "0.1.0"
