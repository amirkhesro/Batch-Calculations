"""Plain text report of a calculated batch."""

from __future__ import annotations

from .calculate import Batch
from .formula import format_composition

def print_report(batch: Batch) -> None:
    """Print the composition, the batch mass in grams, then the raw materials."""
    width = 78
    print()
    print("=" * width)
    print(f"  {format_composition(batch.atoms)}")
    print("=" * width)
    print(f"  Composition entered : {batch.composition}")
    print(f"  Formula weight      : {batch.formula_weight:.3f} g/mol")
    print(f"  Target batch mass   : {batch.target_mass_g:.4f} g")
    print(f"  Moles of product    : {batch.moles:.6f} mol")
    if batch.notes:
        print(f"  Notes               : {batch.notes}")

    print()
    print("  RAW MATERIALS REQUIRED")
    print("  " + "-" * (width - 2))
    print(f"  {'Raw material':<28}{'Formula':<12}{'M (g/mol)':>11}{'Purity':>9}{'Mass (g)':>12}")
    print("  " + "-" * (width - 2))
    for reagent in batch.reagents:
        print(
            f"  {reagent.name[:27]:<28}{reagent.formula:<12}{reagent.molar_mass:>11.3f}"
            f"{reagent.purity:>9.4f}{reagent.mass_g:>12.4f}"
        )
    print("  " + "-" * (width - 2))
    print(f"  {'Total weighed mass':<60}{batch.total_reagent_mass_g:>12.4f}")
    loss = batch.total_reagent_mass_g - batch.target_mass_g
    print(
        f"  {'Mass lost on firing (CO2, H2O, ...)':<60}{loss:>12.4f}"
        if loss > 1e-9
        else f"  {'Mass change on firing':<60}{loss:>12.4f}"
    )

    for warning in batch.warnings:
        print(f"\n  ! {warning}")
    print()
