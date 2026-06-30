#!/usr/bin/env python3
"""
UserForge CLI
-------------
Command-line interface for the UserForge local username generator.
100% offline — generates candidate strings only, no network requests.

Examples:
    python cli.py -l 3 -m letters --pronounceable -n 50
    python cli.py -l 4 -m mixed -n 200 --starts-with k --out results
    python cli.py -l 3 -l 4 -m letters -n 30          # multiple lengths at once
    python cli.py -l 3 --charset "kxzqj" -n 20         # custom character pool
"""

import argparse
import sys

from engine import generate_usernames, generate_multi_length, estimate_space, save_txt, save_json

# ANSI colors (degrade gracefully on terminals without support)
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
GREEN = "\033[92m"
DIM = "\033[2m"


def banner():
    print(f"{PURPLE}{BOLD}")
    print("  ⚒  UserForge CLI")
    print(f"{RESET}{DIM}  Local username candidate generator — offline only{RESET}\n")


def build_parser():
    p = argparse.ArgumentParser(
        prog="userforge",
        description="Generate candidate short usernames locally (no network).",
    )
    p.add_argument("-l", "--length", type=int, action="append", choices=[3, 4],
                    help="Username length (3 or 4). Repeatable: -l 3 -l 4")
    p.add_argument("-m", "--mode", choices=["letters", "digits", "mixed"], default="letters",
                    help="Character set to use (default: letters)")
    p.add_argument("-n", "--amount", type=int, default=100,
                    help="Number of candidates to generate per length (default: 100)")
    p.add_argument("--pronounceable", action="store_true",
                    help="Use consonant/vowel alternating pattern (letters mode only)")
    p.add_argument("--starts-with", default="", help="Filter: must start with this string")
    p.add_argument("--ends-with", default="", help="Filter: must end with this string")
    p.add_argument("--contains", default="", help="Filter: must contain this substring")
    p.add_argument("--exclude", default="", help="Characters to exclude from generation")
    p.add_argument("--charset", default="", help="Custom character pool (overrides --mode)")
    p.add_argument("--seed", default=None, help="Seed for reproducible output")
    p.add_argument("--out", default="", help="Base filename to export results to (without extension)")
    p.add_argument("--format", choices=["txt", "json", "both"], default="txt",
                    help="Export format if --out is given (default: txt)")
    p.add_argument("--stats", action="store_true", help="Show search-space statistics and exit")
    p.add_argument("--quiet", action="store_true", help="Suppress banner and extra output")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colors (for piping/redirecting output)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    lengths = args.length or [3]

    if args.no_color or not sys.stdout.isatty():
        global RESET, BOLD, CYAN, PURPLE, GREEN, DIM
        RESET = BOLD = CYAN = PURPLE = GREEN = DIM = ""

    if not args.quiet:
        banner()

    if args.stats:
        for length in lengths:
            space = estimate_space(length, args.mode, args.pronounceable, args.charset)
            print(f"{CYAN}Length {length}{RESET} ({args.mode}{' / pronounceable' if args.pronounceable else ''}): "
                  f"{GREEN}{space:,}{RESET} possible combinations")
        return 0

    seed = args.seed
    if seed is not None:
        try:
            seed = int(seed)
        except ValueError:
            pass  # allow string seeds too

    results_by_length = generate_multi_length(
        lengths,
        amount=args.amount,
        mode=args.mode,
        pronounceable=args.pronounceable,
        starts_with=args.starts_with,
        ends_with=args.ends_with,
        contains=args.contains,
        exclude_chars=args.exclude,
        custom_charset=args.charset,
        seed=seed,
    )

    total = 0
    for length, results in results_by_length.items():
        if not args.quiet:
            print(f"{BOLD}{CYAN}── Length {length} ── {len(results)} candidates{RESET}")
        for u in results:
            print(f"@{u}")
        if not args.quiet:
            print()
        total += len(results)

        if args.out:
            suffix = f"_{length}" if len(lengths) > 1 else ""
            base = f"{args.out}{suffix}"
            if args.format in ("txt", "both"):
                save_txt(results, f"{base}.txt")
                if not args.quiet:
                    print(f"{GREEN}Saved →{RESET} {base}.txt")
            if args.format in ("json", "both"):
                save_json(results, f"{base}.json")
                if not args.quiet:
                    print(f"{GREEN}Saved →{RESET} {base}.json")

    if not args.quiet:
        print(f"\n{DIM}Total generated: {total}. Remember to verify availability manually in WhatsApp.{RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
