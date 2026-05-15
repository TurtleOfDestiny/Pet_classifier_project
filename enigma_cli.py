"""
Enigma Machine CLI

Usage examples:

  Encrypt a message:
    python enigma_cli.py encrypt --rotors I II III --reflector B \\
        --positions A A A --text "ATTACK AT DAWN"

  Decrypt a message (same command — Enigma is symmetric):
    python enigma_cli.py decrypt --rotors I II III --reflector B \\
        --positions A A A --text "MFNCZB"

  Crack a message with a known crib:
    python enigma_cli.py crack --text "MFNCZB" --crib "ATTACK"

  Crack without a crib (slower — uses Index of Coincidence):
    python enigma_cli.py crack --text "MFNCZB" --rotors I II III --reflectors B
"""

import argparse
import sys
from typing import List

from enigma_machine import EnigmaMachine, ROTOR_DATA, REFLECTOR_DATA
from enigma_breaker import crack_enigma, index_of_coincidence, chi_squared_score

ROTOR_CHOICES = list(ROTOR_DATA.keys())
REFLECTOR_CHOICES = list(REFLECTOR_DATA.keys())


def _parse_positions(values: List[str]) -> List[int]:
    result = []
    for v in values:
        v = v.upper()
        if v.isalpha() and len(v) == 1:
            result.append(ord(v) - 65)
        else:
            try:
                n = int(v)
                if not 1 <= n <= 26:
                    raise ValueError
                result.append(n - 1)
            except ValueError:
                print(f"Error: '{v}' is not a valid position (use A-Z or 1-26).")
                sys.exit(1)
    return result


def cmd_encrypt(args):
    positions = _parse_positions(args.positions)
    rings = _parse_positions(args.rings)

    machine = EnigmaMachine(
        rotor_names=args.rotors,
        reflector_name=args.reflector,
        ring_settings=rings,
        start_positions=positions,
        plugboard_pairs=args.plugboard or [],
    )
    result = machine.encrypt(args.text)

    label = 'Encrypted' if args.command == 'encrypt' else 'Decrypted'
    print(f"\n{label}: {result}")
    print(f"Rotors    : {' '.join(args.rotors)}")
    print(f"Reflector : {args.reflector}")
    print(f"Positions : {' '.join(args.positions)}")
    print(f"Rings     : {' '.join(args.rings)}")
    if args.plugboard:
        print(f"Plugboard : {' '.join(args.plugboard)}")


def cmd_crack(args):
    candidates = crack_enigma(
        ciphertext=args.text,
        crib=args.crib,
        top_n=args.top,
        use_reflectors=args.reflectors,
        use_rotors=args.rotors,
        verbose=True,
    )

    if not candidates:
        print("\nNo candidates found.")
        print("Tips:")
        print("  • Use --crib with a word likely in the plaintext.")
        print("  • Expand the rotor/reflector search with --rotors and --reflectors.")
        print("  • The message may be too short for statistical attacks (try >50 chars).")
        return

    print(f"\nTop {len(candidates)} candidate(s):\n")
    for i, c in enumerate(candidates, 1):
        print(f"--- #{i} ---")
        print(f"  Rotors    : {' '.join(c['rotors'])}")
        print(f"  Reflector : {c['reflector']}")
        print(f"  Positions : {' '.join(c['positions'])}")
        print(f"  Rings     : {' '.join(c['ring_settings'])}")
        if 'ioc' in c:
            print(f"  IoC       : {c['ioc']:.4f}")
        print(f"  Chi²      : {c['score']:.2f}")
        preview = c['plaintext'][:80]
        if len(c['plaintext']) > 80:
            preview += '…'
        print(f"  Plaintext : {preview}")
        print()


def build_parser():
    parser = argparse.ArgumentParser(
        description='Enigma Machine — WWII cipher simulator and code breaker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', metavar='COMMAND')
    sub.required = True

    # Shared encrypt/decrypt options
    def add_machine_args(p):
        p.add_argument('--rotors', nargs=3, default=['I', 'II', 'III'],
                       metavar='ROTOR', choices=ROTOR_CHOICES,
                       help='Three rotor names left-to-right (default: I II III)')
        p.add_argument('--reflector', default='B', choices=REFLECTOR_CHOICES,
                       help='Reflector (default: B)')
        p.add_argument('--positions', nargs=3, default=['A', 'A', 'A'],
                       metavar='POS',
                       help='Start positions A-Z or 1-26 (default: A A A)')
        p.add_argument('--rings', nargs=3, default=['A', 'A', 'A'],
                       metavar='RING',
                       help='Ring settings A-Z or 1-26 (default: A A A)')
        p.add_argument('--plugboard', nargs='*', metavar='PAIR',
                       help='Plugboard pairs e.g. AB CD EF')
        p.add_argument('--text', required=True, help='Message to process')

    enc = sub.add_parser('encrypt', help='Encrypt a plaintext message')
    add_machine_args(enc)

    dec = sub.add_parser('decrypt', help='Decrypt a ciphertext (identical to encrypt)')
    add_machine_args(dec)

    # Crack command
    crk = sub.add_parser('crack', help='Attempt to find the Enigma settings for a ciphertext')
    crk.add_argument('--text', required=True, help='Ciphertext to crack')
    crk.add_argument('--crib', help='Known plaintext word/phrase (greatly speeds up search)')
    crk.add_argument('--rotors', nargs='+', default=ROTOR_CHOICES,
                     metavar='ROTOR', choices=ROTOR_CHOICES,
                     help='Rotors to try (default: all)')
    crk.add_argument('--reflectors', nargs='+', default=REFLECTOR_CHOICES,
                     metavar='REF', choices=REFLECTOR_CHOICES,
                     help='Reflectors to try (default: all)')
    crk.add_argument('--top', type=int, default=5,
                     help='Number of top candidates to display (default: 5)')

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command in ('encrypt', 'decrypt'):
        cmd_encrypt(args)
    elif args.command == 'crack':
        cmd_crack(args)


if __name__ == '__main__':
    main()
