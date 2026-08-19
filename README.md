# batch-calculations

A batch-weight calculator for solid-state ceramic synthesis. Give it a target
composition and a batch mass, and it tells you how many grams of each raw
material to weigh out. Every run is appended to an Excel log workbook, so
nothing already recorded is ever overwritten.

Written and maintained by Amir Khesro, University of Sheffield.

## What you need before starting

A computer with Python 3.11 or newer. To check, open a terminal (see step 1
below) and run:

    python --version

If Python is missing or too old, install it from https://www.python.org/downloads/
and tick the box that says "Add Python to PATH" during installation.

## Step 1: Open a terminal

On Windows, press the Start key, type "PowerShell" and press Enter.
On macOS, open the Terminal app. On Linux, open your usual terminal.

Do not run PowerShell as administrator. It is not needed and it starts you in
a protected system folder where the log file cannot be written.

## Step 2: Install the package (once per computer)

Copy this line into the terminal and press Enter:

    pip install git+https://github.com/amirkhesro/Batch-Calculations.git

## Step 3: Check it works

    batchcalc --version

You should see a version number, for example `batchcalc 0.2.0`. If PowerShell
says the command is not recognised, close the terminal, open a new one and try
again. If it still fails, run it as `python -m batch_calculations.cli --version`
and use that form throughout.

## Step 4: Move to a folder where you keep lab records

The Excel log is written to whatever folder the terminal is currently in, so
go somewhere sensible first:

    cd $HOME\Documents

## Step 5: Run your first calculation

The pattern is: composition in quotes, then batch mass in grams.

    batchcalc "Ba0.85Ca0.15Zr0.1Ti0.9O3" 30

You get the formula weight, the moles of product, and a weighing table listing
grams of each raw material, the total mass to weigh, and the mass that will be
lost on firing as CO2. The run is also appended to `stoichiometry_log.xlsx`
in the current folder.

## Step 6: Enter the purity of your reagents

Read the assay from each bottle and pass it as a fraction, one flag per
reagent:

    batchcalc "Ba0.85Ca0.15Zr0.1Ti0.9O3" 30 --purity BaCO3=0.995 --purity TiO2=0.999

The calculator weighs those reagents proportionally heavier so that the moles
of cation delivered are exactly right. Enter purities for any batch that will
be measured, compared or published. It is the differences in purity between
reagents that shift your cation ratios, not the absolute values, so a purity
common to every bottle changes nothing while a mismatch between two bottles
shifts stoichiometry by roughly the size of the mismatch.

## Step 7: Other options you will use

Choose a different raw material for an element (defaults are carbonates for
alkalis and alkaline earths, oxides for most other cations):

    batchcalc "BaTiO3" 10 --use Ba=BaO

Store processing notes with the batch record:

    batchcalc "BaTiO3" 10 --note "calcine 1200 C, 4 h"

Quick check without saving anything:

    batchcalc "BaTiO3" 10 --no-log

Send the log to a specific file:

    batchcalc "BaTiO3" 10 --log C:\Users\you\Documents\my_log.xlsx

Assume a single purity for every reagent you have not named individually
(the default is 1.0, meaning everything is treated as 100 per cent pure):

    batchcalc "BaTiO3" 10 --default-purity 0.99

## Writing formulas

Decimal subscripts, brackets and hydrate notation are all accepted:
`Ba0.5Sr0.5TiO3`, `La(OH)3`, `CuSO4*5H2O`. Spaces are ignored. Write hydrates
with `*` or a middot, not a bare dot. Be careful to type the letter O for
oxygen, not the digit zero.

## Assumptions

All precursors are treated as dry, with no water of crystallisation.
Impurities are assumed inert: the purity correction fixes the moles of cation
delivered, and the impurity mass simply ends up in the batch. Oxygen, carbon,
hydrogen and nitrogen are supplied by the precursors or the furnace atmosphere
and never need a raw material of their own. Reagents are taken as 100 per cent
pure unless stated, so batches stay comparable run to run. The calculator
cross-checks what the chosen reagents deliver against what the formula wants
and prints a warning for anything missing, over-supplied or under-supplied.

## The log workbook

Each run appends one row to a "Batches" sheet and one row per raw material to
a "Raw Materials" sheet, with a shared batch ID, a timestamp, and the purities
used. If the workbook is open in Excel and locked, the run is saved to a
timestamped fallback file instead and the message tells you where.

## Troubleshooting

"Permission denied" when saving the log: your terminal is in a protected
folder, usually C:\WINDOWS\system32. Run `cd $HOME\Documents` and try again.

"batchcalc is not recognised": open a fresh terminal, or use
`python -m batch_calculations.cli` instead.

"No default raw material for X": the element has no default precursor in the
built-in table. Tell the calculator what to use, for example `--use X=XO2`.

## Updating

When the code improves, update with:

    pip install --upgrade --force-reinstall git+https://github.com/amirkhesro/Batch-Calculations.git

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

Pass `precursor_choices` to pick the raw material for an element, the Python
equivalent of `--use`. The defaults are defined in `batch_calculations/data.py`.

## Development

    uv sync
    uv run pytest
    uv run ruff check .

Or, without uv, `pip install -e .` installs the package in editable form and
`pytest` and `ruff check .` then run directly.

The test suite includes batches verified against independent hand
calculations.

## Licence

MIT. See the LICENSE file.
