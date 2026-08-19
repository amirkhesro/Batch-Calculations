"""Parser and molar mass tests, checked against hand calculations."""

import pytest

from batch_calculations import molar_mass, parse_formula
from batch_calculations.formula import format_composition


def test_simple_formula():
    assert parse_formula("BaTiO3") == {"Ba": 1.0, "Ti": 1.0, "O": 3.0}


def test_decimal_subscripts():
    atoms = parse_formula("Ba0.5Sr0.5TiO3")
    assert atoms["Ba"] == pytest.approx(0.5)
    assert atoms["Sr"] == pytest.approx(0.5)
    assert atoms["Ti"] == pytest.approx(1.0)
    assert atoms["O"] == pytest.approx(3.0)


def test_spaces_ignored():
    assert parse_formula("Ba 0.5 Sr 0.5 Ti O3") == parse_formula("Ba0.5Sr0.5TiO3")


def test_brackets():
    atoms = parse_formula("La(OH)3")
    assert atoms == {"La": 1.0, "O": 3.0, "H": 3.0}


def test_nested_brackets():
    atoms = parse_formula("Ca(Al(OH)4)2")
    assert atoms == {"Ca": 1.0, "Al": 2.0, "O": 8.0, "H": 8.0}


def test_hydrate_star():
    atoms = parse_formula("CuSO4*5H2O")
    assert atoms == {"Cu": 1.0, "S": 1.0, "O": 9.0, "H": 10.0}


def test_unknown_element_rejected():
    with pytest.raises(ValueError):
        parse_formula("Xx2O3")


def test_unbalanced_brackets_rejected():
    with pytest.raises(ValueError):
        parse_formula("Ba(TiO3")


def test_molar_mass_batio3():
    # 137.327 + 47.867 + 3 * 15.999 = 233.191
    assert molar_mass("BaTiO3") == pytest.approx(233.191, abs=1e-3)


def test_molar_mass_baco3():
    # 137.327 + 12.011 + 3 * 15.999 = 197.335
    assert molar_mass("BaCO3") == pytest.approx(197.335, abs=1e-3)


def test_format_composition_roundtrip():
    text = format_composition(parse_formula("Ba0.5Sr0.5TiO3"))
    assert parse_formula(text) == parse_formula("Ba0.5Sr0.5TiO3")
