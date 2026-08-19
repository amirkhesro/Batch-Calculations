"""Stoichiometry and batch-weight calculations for solid-state ceramic synthesis.

Typical use:

    from batch_calculations import calculate_batch, print_report

    batch = calculate_batch("Ba0.85Ca0.15Zr0.1Ti0.9O3", 30.0,
                            purities={"BaCO3": 0.995})
    print_report(batch)
"""

from __future__ import annotations

__version__ = "0.2.0"

from .calculate import Batch, Reagent, calculate_batch
from .data import ATOMIC_MASS, DEFAULT_PRECURSOR, PRECURSOR_NAME
from .excel_log import append_to_log
from .formula import format_composition, molar_mass, parse_formula
from .report import print_report

__all__ = [
    "ATOMIC_MASS",
    "Batch",
    "DEFAULT_PRECURSOR",
    "PRECURSOR_NAME",
    "Reagent",
    "append_to_log",
    "calculate_batch",
    "format_composition",
    "molar_mass",
    "parse_formula",
    "print_report",
    "__version__",
]
