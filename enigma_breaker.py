"""
Enigma Code Breaker

Implements a brute-force statistical attack to recover Enigma machine settings
from ciphertext. Uses two scoring strategies:

1. Crib attack: if a likely plaintext word (crib) is known, search for settings
   that produce it in the decrypted output, then rank by chi-squared fitness.

2. Index of Coincidence (IoC) attack: without a crib, filter candidates whose
   decrypted output has an IoC close to English (≈0.065 vs. random ≈0.038),
   then rank by chi-squared fitness against English letter frequencies.

Ring settings add a third dimension (26^3) to the search space and are
prohibitively slow to brute-force in Python without a crib. The breaker fixes
ring settings at AAA by default; pass known ring settings if available.
"""

import itertools
from typing import List, Optional, Tuple

from enigma_machine import EnigmaMachine, ROTOR_DATA, REFLECTOR_DATA

# English single-letter frequencies (from corpus analysis)
ENGLISH_FREQ = {
    'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253,
    'E': 0.12702, 'F': 0.02228, 'G': 0.02015, 'H': 0.06094,
    'I': 0.06966, 'J': 0.00153, 'K': 0.00772, 'L': 0.04025,
    'M': 0.02406, 'N': 0.06749, 'O': 0.07507, 'P': 0.01929,
    'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
    'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150,
    'Y': 0.01974, 'Z': 0.00074,
}

# IoC for natural English text
ENGLISH_IOC = 0.065


def index_of_coincidence(text: str) -> float:
    """Compute the Index of Coincidence for a string of uppercase letters."""
    n = len(text)
    if n < 2:
        return 0.0
    counts = [text.count(chr(i + 65)) for i in range(26)]
    return sum(c * (c - 1) for c in counts) / (n * (n - 1))


def chi_squared_score(text: str) -> float:
    """
    Compute chi-squared statistic comparing letter distribution to English.
    Lower score = more English-like.
    """
    n = len(text)
    if n == 0:
        return float('inf')
    score = 0.0
    for i in range(26):
        observed = text.count(chr(i + 65))
        expected = ENGLISH_FREQ[chr(i + 65)] * n
        if expected > 0:
            score += (observed - expected) ** 2 / expected
    return score


def _decrypt(
    ciphertext: str,
    rotors: List[str],
    reflector: str,
    positions: Tuple[int, int, int],
    ring_settings: Tuple[int, int, int],
) -> str:
    machine = EnigmaMachine(
        rotor_names=rotors,
        reflector_name=reflector,
        ring_settings=list(ring_settings),
        start_positions=list(positions),
    )
    return machine.encrypt(ciphertext)


def crack_enigma(
    ciphertext: str,
    crib: Optional[str] = None,
    top_n: int = 10,
    use_reflectors: Optional[List[str]] = None,
    use_rotors: Optional[List[str]] = None,
    ring_settings: Tuple[int, int, int] = (0, 0, 0),
    ioc_threshold: float = 0.055,
    verbose: bool = True,
) -> List[dict]:
    """
    Attempt to crack an Enigma-encrypted message by brute-forcing rotor
    combinations and start positions.

    Args:
        ciphertext:     Encrypted message (non-alpha characters are ignored).
        crib:           Known plaintext word/phrase to search for (optional).
        top_n:          Maximum number of candidate results to return.
        use_reflectors: Reflectors to try (default: ['B', 'C']).
        use_rotors:     Rotors to choose from (default: all five I-V).
        ring_settings:  Fixed ring settings to use (default: AAA = (0,0,0)).
        ioc_threshold:  Minimum IoC to keep a candidate when no crib is given.
        verbose:        Print progress to stdout.

    Returns:
        List of candidate dicts sorted best-first, each with keys:
        rotors, reflector, positions, ring_settings, plaintext, score[, ioc].
    """
    ciphertext = ''.join(c for c in ciphertext.upper() if c.isalpha())
    if not ciphertext:
        return []

    if use_reflectors is None:
        use_reflectors = list(REFLECTOR_DATA.keys())
    if use_rotors is None:
        use_rotors = list(ROTOR_DATA.keys())

    if crib:
        crib = ''.join(c for c in crib.upper() if c.isalpha())

    rotor_combos = list(itertools.permutations(use_rotors, 3))
    total = len(rotor_combos) * len(use_reflectors) * (26 ** 3)

    if verbose:
        print(f"Searching {total:,} combinations "
              f"({'with' if crib else 'without'} crib)...")

    candidates = []
    tested = 0
    milestone = max(total // 20, 1)

    for rotors in rotor_combos:
        for reflector in use_reflectors:
            for pos in itertools.product(range(26), repeat=3):
                plaintext = _decrypt(ciphertext, list(rotors), reflector,
                                     pos, ring_settings)

                if crib:
                    if crib in plaintext:
                        candidates.append({
                            'rotors': list(rotors),
                            'reflector': reflector,
                            'positions': [chr(p + 65) for p in pos],
                            'ring_settings': [chr(r + 65) for r in ring_settings],
                            'plaintext': plaintext,
                            'score': chi_squared_score(plaintext),
                        })
                else:
                    ioc = index_of_coincidence(plaintext)
                    if ioc >= ioc_threshold:
                        candidates.append({
                            'rotors': list(rotors),
                            'reflector': reflector,
                            'positions': [chr(p + 65) for p in pos],
                            'ring_settings': [chr(r + 65) for r in ring_settings],
                            'plaintext': plaintext,
                            'score': chi_squared_score(plaintext),
                            'ioc': round(ioc, 4),
                        })

                tested += 1
                if verbose and tested % milestone == 0:
                    pct = 100 * tested / total
                    print(f"  {tested:,}/{total:,} ({pct:.0f}%) — "
                          f"{len(candidates)} candidate(s) so far")

    candidates.sort(key=lambda c: c['score'])
    if verbose:
        print(f"Done. {len(candidates)} candidate(s) found.")
    return candidates[:top_n]
