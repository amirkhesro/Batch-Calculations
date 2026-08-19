# batch-calculations

Stoichiometry and batch-weight calculations for solid-state ceramic synthesis.

Give it a target composition and a batch mass, and it works out how many grams
of each raw material to weigh out. Every run is appended to an Excel log
workbook, so nothing already recorded is ever overwritten.

## Install

Directly from GitHub:

    pip install git+https://github.com/amirkhesro/batch-calculations.git

For a private repository, authenticate first (for example with the GitHub CLI,
`gh auth login`) or use an SSH remote:

    pip install git+ssh://git@github.com/amirkhesro/batch-calculations.git

Or, working on the code itself, clone the repository and run `uv sync` (or
`pip install -e .`).

## Command line use

    batchcalc "Sr0.38La0.12Ba0.5Ti0.12Nb1.88O6" 30
    batchcalc "Ba0.5Sr0.5TiO3" 25 --use Ti=TiO2 --purity Nb2O5=0.998
    batchcalc "BaTiO3" 10 --note "calcine 1200 C, 4 h"
    batchcalc "BaTiO3" 10 --no-log

Options:

    --use EL=FORMULA          raw material for an element, e.g. --use Ti=TiO2
    --purity FORMULA=FRACTION purity of a raw material, e.g. --purity BaCO3=0.995
    --default-purity FRACTION purity assumed when not given (default 1.0)
    --note TEXT               free text stored with the batch
    --log FILE                log workbook (default stoichiometry_log.xlsx)
    --no-log                  print only, do not save

## Use from Python

    from batch_calculations import calculate_batch, print_report, append_to_log

    batch = calculate_batch(
        "Ba0.85Ca0.15Zr0.1Ti0.9O3",
        target_mass_g=30.0,
        purities={"BaCO3": 0.995, "CaCO3": 0.990},
    )
    print_report(batch)
    append_to_log(batch, "stoichiometry_log.xlsx")

`calculate_batch` returns a `Batch` dataclass carrying the parsed composition,
formula weight, moles of product, and one `Reagent` per raw material with its
molar mass, purity and mass to weigh.

## Assumptions and conventions

All precursors are treated as dry: no water of crystallisation is considered
anywhere. Purity scales the weighed mass, so a reagent recorded at 0.995 purity
is weighed proportionally heavier to deliver the same moles of cation; any
impurity is assumed inert and simply ends up in the batch. Reagents are taken
as 100 per cent pure unless a purity is given, so batches stay comparable run
to run. Oxygen, carbon, hydrogen and nitrogen are supplied by the precursors
or the furnace atmosphere and never need a raw material of their own.

Formulas accept decimal subscripts, nested brackets and hydrate notation:
`Ba0.5Sr0.5TiO3`, `La(OH)3`, `CuSO4*5H2O`. Write hydrates with `*` or the
middot, not a bare dot, so the coefficient is unambiguous.

Default raw materials (carbonates for the alkalis and alkaline earths, oxides
for most other cations) are defined in `batch_calculations/data.py` and can be
overridden per run with `--use` or the `precursor_choices` argument.

The calculation cross checks what the chosen reagents actually deliver against
what the target formula wants, and prints a warning for anything missing,
over supplied or under supplied.

## Log workbook

Each run appends one row to a `Batches` sheet and one row per raw material to
a `Raw Materials` sheet, with a shared batch ID and timestamp. If the workbook
is open in Excel and locked, the run is saved to a timestamped fallback file
instead and the error message tells you where.

## Development

    uv sync
    uv run pytest
    uv run ruff check .
