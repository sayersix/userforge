"""
UserForge — Core Generation Engine
-----------------------------------
Pure local username-candidate generator. No network calls, no external
requests of any kind. Produces unique short username strings based on
configurable rules (length, character pool, pronounceable patterns,
prefix/suffix/contains filters, custom charsets, reproducible seeds).
"""

import string
import random
import json

LOWER = string.ascii_lowercase
DIGITS = string.digits
VOWELS = "aeiou"
CONSONANTS = "".join(c for c in LOWER if c not in VOWELS)


def max_possible(length: int, pool_size: int) -> int:
    return pool_size ** length


def _pronounceable_pool_size(length: int) -> int:
    c_count = (length + 1) // 2
    v_count = length // 2
    return (len(CONSONANTS) ** c_count) * (len(VOWELS) ** v_count)


def resolve_pool(mode: str, custom_charset: str = "") -> str:
    if custom_charset:
        return "".join(dict.fromkeys(custom_charset))  # dedupe, preserve order
    if mode == "letters":
        return LOWER
    if mode == "digits":
        return DIGITS
    return LOWER + DIGITS  # mixed


def estimate_space(length: int, mode: str, pronounceable: bool, custom_charset: str = "") -> int:
    """Return the theoretical max number of unique combinations for given settings."""
    if pronounceable and mode == "letters" and not custom_charset:
        return _pronounceable_pool_size(length)
    pool = resolve_pool(mode, custom_charset)
    return max_possible(length, len(pool))


def generate_usernames(
    amount: int = 100,
    length: int = 3,
    mode: str = "letters",
    pronounceable: bool = False,
    starts_with: str = "",
    ends_with: str = "",
    contains: str = "",
    exclude_chars: str = "",
    custom_charset: str = "",
    seed=None,
):
    """
    Generate a unique set of candidate usernames.

    mode: "letters" | "digits" | "mixed"  (ignored if custom_charset given)
    pronounceable: alternate consonant/vowel pattern (letters mode only)
    starts_with / ends_with / contains: optional filters (case-insensitive)
    exclude_chars: characters to exclude entirely from generation
    custom_charset: override the pool entirely with your own character set
    seed: optional int/str for reproducible output
    """
    rng = random.Random(seed) if seed is not None else random

    starts_with = starts_with.lower().strip()
    ends_with = ends_with.lower().strip()
    contains = contains.lower().strip()
    exclude_set = set(exclude_chars.lower().strip())

    results = set()
    attempts = 0
    max_attempts = 500_000  # safety cap so callers never hard-lock

    if pronounceable and mode == "letters" and not custom_charset:
        consonants = "".join(c for c in CONSONANTS if c not in exclude_set) or CONSONANTS
        vowels = "".join(c for c in VOWELS if c not in exclude_set) or VOWELS
        cap = _pronounceable_pool_size(length)
        amount = min(amount, cap)
        while len(results) < amount and attempts < max_attempts:
            attempts += 1
            chars = []
            for i in range(length):
                chars.append(rng.choice(consonants) if i % 2 == 0 else rng.choice(vowels))
            u = "".join(chars)
            if starts_with and not u.startswith(starts_with):
                continue
            if ends_with and not u.endswith(ends_with):
                continue
            if contains and contains not in u:
                continue
            results.add(u)
        return sorted(results)

    pool = resolve_pool(mode, custom_charset)
    pool = "".join(c for c in pool if c not in exclude_set) or pool
    cap = max_possible(length, len(pool))
    amount = min(amount, cap)

    while len(results) < amount and attempts < max_attempts:
        attempts += 1
        u = "".join(rng.choice(pool) for _ in range(length))
        if starts_with and not u.startswith(starts_with):
            continue
        if ends_with and not u.endswith(ends_with):
            continue
        if contains and contains not in u:
            continue
        results.add(u)

    return sorted(results)


def generate_multi_length(lengths, **kwargs):
    """Generate across multiple lengths at once, e.g. lengths=[3, 4].
    `amount` in kwargs is applied per-length."""
    combined = {}
    for length in lengths:
        combined[length] = generate_usernames(length=length, **kwargs)
    return combined


def save_txt(usernames, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for u in usernames:
            f.write("@" + u + "\n")


def save_json(usernames, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(usernames, f, ensure_ascii=False, indent=2)
