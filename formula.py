"""Chemical formula parsing and molar mass calculation."""

from __future__ import annotations

import re

from .data import ATOMIC_MASS

_TOKEN = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)|(\()|(\)(\d*\.?\d*))")


def parse_formula(formula: str) -> dict[str, float]:
    """Turn a formula string into {element: atoms per formula unit}.

    Handles decimals, nested brackets and hydrates:
    ``Ba0.5Sr0.5TiO3``, ``La(OH)3``, ``Y2O3 * 3 H2O``, ``CuSO4 · 5 H2O``.

    A ``.`` between two digits is always read as a decimal point, since decimal
    subscripts are the common case here - write hydrates with ``*`` or ``·``
    (``CuSO4*5H2O``), not ``CuSO4.5H2O``, so the coefficient is unambiguous.
    """
    text = formula.replace(" ", "").replace("[", "(").replace("]", ")")

    # Hydrate notation: middot/asterisk always separates; a bare dot only when
    # it is not sitting between two digits (i.e. it is not a decimal point).
    parts = re.split(r"[·∙*]|(?<!\d)\.|\.(?!\d)", text)
    parts = [p for p in parts if p]

    total: dict[str, float] = {}
    for part in parts:
        lead = re.match(r"^(\d+\.?\d*)(?=[A-Z(])", part)
        multiplier = float(lead.group(1)) if lead else 1.0
        if lead:
            part = part[lead.end() :]
        for element, count in _parse_group(part, formula).items():
            total[element] = total.get(element, 0.0) + count * multiplier

    if not total:
        raise ValueError(f"No elements found in formula {formula!r}.")
    unknown = sorted(e for e in total if e not in ATOMIC_MASS)
    if unknown:
        raise ValueError(f"Unknown element(s) in {formula!r}: {', '.join(unknown)}")
    return total


def _parse_group(text: str, original: str) -> dict[str, float]:
    """Recursive-descent walk over one bracketed formula fragment."""
    stack: list[dict[str, float]] = [{}]
    pos = 0
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if match is None or match.end() == pos:
            raise ValueError(f"Could not parse {original!r} at {text[pos:]!r}.")
        pos = match.end()

        if match.group(3):  # opening bracket
            stack.append({})
        elif match.group(4):  # closing bracket + count
            count = float(match.group(5)) if match.group(5) else 1.0
            if len(stack) == 1:
                raise ValueError(f"Unbalanced brackets in {original!r}.")
            group = stack.pop()
            for element, amount in group.items():
                stack[-1][element] = stack[-1].get(element, 0.0) + amount * count
        else:  # element symbol + count
            element = match.group(1)
            count = float(match.group(2)) if match.group(2) else 1.0
            stack[-1][element] = stack[-1].get(element, 0.0) + count

    if len(stack) != 1:
        raise ValueError(f"Unbalanced brackets in {original!r}.")
    return stack[0]


def molar_mass(formula: str | dict[str, float]) -> float:
    """Molar mass in g/mol of a formula string or an already-parsed composition."""
    atoms = parse_formula(formula) if isinstance(formula, str) else formula
    return sum(count * ATOMIC_MASS[element] for element, count in atoms.items())


def format_composition(atoms: dict[str, float]) -> str:
    """Tidy one-line rendering of a parsed composition."""

    def fmt(value: float) -> str:
        return "" if value == 1 else f"{value:g}"

    return "".join(f"{element}{fmt(count)}" for element, count in atoms.items())
