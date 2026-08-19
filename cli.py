"""Command line interface.

Examples:

    batchcalc "Sr0.38La0.12Ba0.5Ti0.12Nb1.88O6" 30
    batchcalc "Ba0.5Sr0.5TiO3" 25 --use Ti=TiO2 --purity Nb2O5=0.998
    batchcalc "BaTiO3" 10 --note "calcine 1200 C, 4 h"
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from . import __version__
from .calculate import DEFAULT_PURITY, calculate_batch
from .excel_log import DEFAULT_LOG_FILE, append_to_log
from .report import print_report


def _parse_pairs(values: list[str] | None, name: str, cast: Callable[[str], object] = str) -> dict:
    pairs = {}
    for item in values or []:
        if "=" not in item:
            raise SystemExit(f"--{name} expects KEY=VALUE, got {item!r}.")
        key, _, value = item.partition("=")
        pairs[key.strip()] = cast(value.strip())
    return pairs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="batchcalc",
        description="Batch-weight calculator for any ceramic composition.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("composition", help="target formula, e.g. Ba0.5Sr0.5TiO3")
    parser.add_argument("mass", type=float, help="batch mass in grams")
    parser.add_argument(
        "--use",
        action="append",
        metavar="EL=FORMULA",
        help="raw material for an element, e.g. --use Ti=TiO2",
    )
    parser.add_argument(
        "--purity",
        action="append",
        metavar="FORMULA=FRACTION",
        help="purity of a raw material, e.g. --purity Nb2O5=0.998",
    )
    parser.add_argument(
        "--default-purity",
        type=float,
        default=DEFAULT_PURITY,
        help=f"purity used when not given (default {DEFAULT_PURITY})",
    )
    parser.add_argument("--note", default="", help="free text stored with the batch")
    parser.add_argument("--log", default=DEFAULT_LOG_FILE, help=f"log workbook (default {DEFAULT_LOG_FILE})")
    parser.add_argument("--no-log", action="store_true", help="print only, do not save")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        batch = calculate_batch(
            composition=args.composition,
            target_mass_g=args.mass,
            precursor_choices=_parse_pairs(args.use, "use"),
            purities=_parse_pairs(args.purity, "purity", float),
            default_purity=args.default_purity,
            notes=args.note,
        )
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print_report(batch)

    if not args.no_log:
        try:
            path, batch_id = append_to_log(batch, args.log)
        except PermissionError as error:
            print(f"  ! {error}\n")
            return 1
        print(f"  Appended as batch {batch_id} to {path} (sheets 'Batches' and 'Raw Materials').\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
