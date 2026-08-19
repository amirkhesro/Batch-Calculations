"""Batch calculation tests against fully hand-checked numbers."""

import pytest

from batch_calculations import calculate_batch

# Hand-checked atomic masses (IUPAC), g/mol
BA, CA, ZR, TI, SR, O, C, NB = (
    137.327, 40.078, 91.224, 47.867, 87.62, 15.999, 12.011, 92.906,
)


def test_batio3_from_carbonate_and_oxide():
    m_batio3 = BA + TI + 3 * O
    moles = 10.0 / m_batio3
    batch = calculate_batch("BaTiO3", 10.0)

    assert batch.formula_weight == pytest.approx(m_batio3, abs=1e-6)
    assert batch.moles == pytest.approx(moles, rel=1e-12)
    by_formula = {r.formula: r for r in batch.reagents}
    assert set(by_formula) == {"BaCO3", "TiO2"}
    assert by_formula["BaCO3"].mass_g == pytest.approx(moles * (BA + C + 3 * O), rel=1e-9)
    assert by_formula["TiO2"].mass_g == pytest.approx(moles * (TI + 2 * O), rel=1e-9)
    assert not batch.warnings


def test_purity_scales_weighed_mass():
    plain = calculate_batch("BaTiO3", 10.0)
    corrected = calculate_batch("BaTiO3", 10.0, purities={"BaCO3": 0.995})
    m = {r.formula: r.mass_g for r in plain.reagents}
    c = {r.formula: r.mass_g for r in corrected.reagents}
    assert c["BaCO3"] == pytest.approx(m["BaCO3"] / 0.995, rel=1e-12)
    assert c["TiO2"] == pytest.approx(m["TiO2"], rel=1e-12)


def test_default_purity_applies_everywhere():
    batch = calculate_batch("BaTiO3", 10.0, default_purity=0.99)
    plain = calculate_batch("BaTiO3", 10.0)
    for r_corr, r_plain in zip(batch.reagents, plain.reagents):
        assert r_corr.mass_g == pytest.approx(r_plain.mass_g / 0.99, rel=1e-12)


def test_bczt_full_hand_check():
    """Ba0.85Ca0.15Zr0.1Ti0.9O3, 30 g — every reagent mass checked by hand."""
    fw = 0.85 * BA + 0.15 * CA + 0.1 * ZR + 0.9 * TI + 3 * O
    moles = 30.0 / fw
    batch = calculate_batch("Ba0.85Ca0.15Zr0.1Ti0.9O3", 30.0)
    expected = {
        "BaCO3": moles * 0.85 * (BA + C + 3 * O),
        "CaCO3": moles * 0.15 * (CA + C + 3 * O),
        "ZrO2": moles * 0.1 * (ZR + 2 * O),
        "TiO2": moles * 0.9 * (TI + 2 * O),
    }
    got = {r.formula: r.mass_g for r in batch.reagents}
    assert got.keys() == expected.keys()
    for formula, mass in expected.items():
        assert got[formula] == pytest.approx(mass, rel=1e-9), formula
    assert not batch.warnings


def test_precursor_override():
    batch = calculate_batch("BaTiO3", 10.0, precursor_choices={"Ba": "BaO"})
    formulas = {r.formula for r in batch.reagents}
    assert "BaO" in formulas and "BaCO3" not in formulas


def test_mass_lost_on_firing_is_positive_with_carbonates():
    batch = calculate_batch("BaTiO3", 10.0)
    assert batch.total_reagent_mass_g > batch.target_mass_g


def test_missing_precursor_raises():
    with pytest.raises(ValueError, match="No default raw material"):
        calculate_batch("XeO3", 5.0)


def test_invalid_purity_rejected():
    with pytest.raises(ValueError, match="Purity"):
        calculate_batch("BaTiO3", 10.0, purities={"BaCO3": 1.2})


def test_nonpositive_mass_rejected():
    with pytest.raises(ValueError):
        calculate_batch("BaTiO3", 0.0)


def test_shared_precursor_ratio_warning():
    # BaTiO3 as the source of both Ba and Ti for a non 1:1 target must warn.
    batch = calculate_batch(
        "Ba0.5Sr0.5Ti0.9Zr0.1O3", 10.0,
        precursor_choices={"Ba": "BaTiO3", "Ti": "BaTiO3"},
    )
    assert any("BaTiO3" in w for w in batch.warnings)
