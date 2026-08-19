"""The batch calculation itself."""

from __future__ import annotations

from dataclasses import dataclass, field

from .data import DEFAULT_PRECURSOR, PRECURSOR_NAME, VOLATILE_OR_LATTICE
from .formula import molar_mass, parse_formula

DEFAULT_PURITY = 1.0

@dataclass
class Reagent:
    """One raw material to weigh out."""

    name: str
    formula: str
    cations: list[str]
    molar_mass: float
    purity: float
    moles: float
    mass_g: float


@dataclass
class Batch:
    """Everything one run of the calculation produced."""

    composition: str
    atoms: dict[str, float]
    formula_weight: float
    target_mass_g: float
    moles: float
    reagents: list[Reagent]
    notes: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def total_reagent_mass_g(self) -> float:
        return sum(r.mass_g for r in self.reagents)


def calculate_batch(
    composition: str,
    target_mass_g: float,
    precursor_choices: dict[str, str] | None = None,
    purities: dict[str, float] | None = None,
    default_purity: float = DEFAULT_PURITY,
    notes: str = "",
) -> Batch:
    """Work out the raw materials needed for `target_mass_g` of `composition`."""
    if target_mass_g <= 0:
        raise ValueError("Target batch mass must be greater than zero.")

    precursor_choices = {**(precursor_choices or {})}
    purities = purities or {}

    atoms = parse_formula(composition)
    formula_weight = molar_mass(atoms)
    moles_product = target_mass_g / formula_weight

    warnings: list[str] = []

    # 1. Pick a raw material for every element that needs one.
    chosen: dict[str, str] = {}
    for element in atoms:
        if element in precursor_choices:
            chosen[element] = precursor_choices[element]
        elif element in DEFAULT_PRECURSOR:
            chosen[element] = DEFAULT_PRECURSOR[element]
        elif element in VOLATILE_OR_LATTICE:
            continue  # supplied by the oxides/carbonates or by the furnace air
        else:
            raise ValueError(
                f"No default raw material for {element}. Pass one explicitly, "
                f'e.g. PRECURSOR_CHOICES = {{"{element}": "{element}O2"}} '
                f"or --use {element}={element}O2."
            )

    # 2. Group cations that share a raw material (e.g. BaTiO3 supplies Ba and Ti).
    grouped: dict[str, list[str]] = {}
    for element, formula in chosen.items():
        grouped.setdefault(formula, []).append(element)

    reagents: list[Reagent] = []
    for formula, elements in grouped.items():
        reagent_atoms = parse_formula(formula)
        reagent_mass = molar_mass(reagent_atoms)
        purity = purities.get(formula, default_purity)
        if not 0 < purity <= 1:
            raise ValueError(f"Purity for {formula} must be between 0 and 1, got {purity}.")

        demands = {}
        for element in elements:
            per_reagent = reagent_atoms.get(element)
            if not per_reagent:
                raise ValueError(f"{formula} contains no {element}.")
            demands[element] = moles_product * atoms[element] / per_reagent

        moles_reagent = max(demands.values())
        if max(demands.values()) - min(demands.values()) > 1e-9 * moles_reagent:
            detail = ", ".join(f"{e}: {v:.6g} mol" for e, v in demands.items())
            warnings.append(
                f"{formula} supplies {'/'.join(elements)} in a ratio that does not match "
                f"the target ({detail}). Using the largest and leaving the rest in excess - "
                f"add a second raw material for the shortfall."
            )

        reagents.append(
            Reagent(
                name=PRECURSOR_NAME.get(formula, formula),
                formula=formula,
                cations=sorted(elements),
                molar_mass=reagent_mass,
                purity=purity,
                moles=moles_reagent,
                mass_g=moles_reagent * reagent_mass / purity,
            )
        )

    # 3. Balance check: what the reagents actually deliver vs what the target wants.
    #    Catches missing elements, and raw materials that bring in a second cation
    #    on top of the one they were picked for (e.g. BaTiO3 alongside TiO2).
    delivered: dict[str, float] = {}
    for reagent in reagents:
        for element, count in parse_formula(reagent.formula).items():
            delivered[element] = delivered.get(element, 0.0) + reagent.moles * count

    for element in sorted(set(atoms) | set(delivered)):
        if element in VOLATILE_OR_LATTICE:
            continue  # O/C/H/N come and go with the furnace atmosphere
        wanted = moles_product * atoms.get(element, 0.0)
        got = delivered.get(element, 0.0)
        if abs(got - wanted) <= 1e-9 * max(wanted, got, 1e-12):
            continue
        if wanted == 0:
            warnings.append(f"{element} is not in the target but the raw materials add it.")
        elif got == 0:
            warnings.append(f"Nothing in the batch supplies {element}.")
        else:
            warnings.append(
                f"{element} is {'over' if got > wanted else 'under'}-supplied by "
                f"{abs(got - wanted) / wanted:.1%} ({got:.6g} mol delivered vs "
                f"{wanted:.6g} mol wanted) - adjust the raw materials for {element}."
            )

    reagents.sort(key=lambda r: r.name.lower())

    return Batch(
        composition=composition.strip(),
        atoms=atoms,
        formula_weight=formula_weight,
        target_mass_g=target_mass_g,
        moles=moles_product,
        reagents=reagents,
        notes=notes,
        warnings=warnings,
    )
