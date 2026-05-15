"""
Enigma Machine Tests

Verifies correctness of the Enigma simulation against known test vectors
and fundamental properties of the machine.
"""

from enigma_machine import EnigmaMachine
from enigma_breaker import index_of_coincidence, chi_squared_score, crack_enigma

PASS = '\033[92m✓\033[0m'
FAIL = '\033[91m✗\033[0m'


def run(name, fn):
    try:
        fn()
        print(f"{PASS} {name}")
        return True
    except AssertionError as e:
        print(f"{FAIL} {name}: {e}")
        return False
    except Exception as e:
        print(f"{FAIL} {name}: {type(e).__name__}: {e}")
        return False


# ---------------------------------------------------------------------------
# Known test vectors
# ---------------------------------------------------------------------------

def test_known_vector_aaaaa():
    """Rotors I/II/III, reflector B, positions AAA, no plugboard: AAAAA → BDZGO"""
    m = EnigmaMachine(['I', 'II', 'III'], 'B')
    assert m.encrypt('AAAAA') == 'BDZGO', f"Got {m.encrypt('AAAAA')}"


def test_known_vector_b():
    """Verify the second known output character individually."""
    m = EnigmaMachine(['I', 'II', 'III'], 'B')
    result = m.encrypt('AA')
    assert result[1] == 'D', f"Expected second char D, got {result[1]}"


def test_known_vector_with_position():
    """Rotors I/II/III, reflector B, position QEV (notch positions): verify stepping."""
    m = EnigmaMachine(['I', 'II', 'III'], 'B', start_positions=[16, 4, 21])
    result = m.encrypt('A')
    assert isinstance(result, str) and len(result) == 1


# ---------------------------------------------------------------------------
# Fundamental properties
# ---------------------------------------------------------------------------

def test_symmetric():
    """Encrypting the ciphertext returns the original plaintext."""
    plaintext = 'HELLOENIGMAWORLD'
    m1 = EnigmaMachine(['I', 'II', 'III'], 'B', start_positions=[3, 14, 21])
    ciphertext = m1.encrypt(plaintext)

    m2 = EnigmaMachine(['I', 'II', 'III'], 'B', start_positions=[3, 14, 21])
    recovered = m2.encrypt(ciphertext)

    assert recovered == plaintext, f"Expected {plaintext}, got {recovered}"


def test_no_letter_self_encrypts():
    """Enigma never encrypts a letter to itself (a key cryptographic property)."""
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        m = EnigmaMachine(['I', 'II', 'III'], 'B')
        result = m.encrypt(char)
        assert result != char, f"Letter {char} mapped to itself"


def test_plugboard_symmetric():
    """Plugboard swaps are applied twice (in and out), preserving symmetry."""
    pairs = ['AB', 'CD', 'EF']
    m1 = EnigmaMachine(['I', 'II', 'III'], 'B', plugboard_pairs=pairs)
    ciphertext = m1.encrypt('SECRETMESSAGE')

    m2 = EnigmaMachine(['I', 'II', 'III'], 'B', plugboard_pairs=pairs)
    recovered = m2.encrypt(ciphertext)
    assert recovered == 'SECRETMESSAGE'


def test_plugboard_changes_output():
    """Plugboard alters the output compared to no plugboard."""
    m1 = EnigmaMachine(['I', 'II', 'III'], 'B')
    m2 = EnigmaMachine(['I', 'II', 'III'], 'B', plugboard_pairs=['AB'])
    assert m1.encrypt('HELLO') != m2.encrypt('HELLO')


def test_ring_setting_changes_output():
    """Different ring settings produce different ciphertexts."""
    m1 = EnigmaMachine(['I', 'II', 'III'], 'B', ring_settings=[0, 0, 0])
    m2 = EnigmaMachine(['I', 'II', 'III'], 'B', ring_settings=[1, 0, 0])
    assert m1.encrypt('HELLO') != m2.encrypt('HELLO')


def test_different_rotors_differ():
    """Different rotor orders produce different outputs."""
    m1 = EnigmaMachine(['I', 'II', 'III'], 'B')
    m2 = EnigmaMachine(['III', 'II', 'I'], 'B')
    assert m1.encrypt('HELLO') != m2.encrypt('HELLO')


def test_reflectors_differ():
    """Reflector B and C produce different outputs."""
    m1 = EnigmaMachine(['I', 'II', 'III'], 'B')
    m2 = EnigmaMachine(['I', 'II', 'III'], 'C')
    assert m1.encrypt('HELLO') != m2.encrypt('HELLO')


def test_non_alpha_passthrough():
    """Non-alphabetic characters are passed through unchanged."""
    m = EnigmaMachine(['I', 'II', 'III'], 'B')
    # encrypt() strips non-alpha, so test encrypt_char directly
    m._step_rotors()
    assert m.encrypt_char('1') == '1'
    assert m.encrypt_char(' ') == ' '


def test_double_stepping():
    """Verify the double-stepping anomaly triggers correctly.

    Start: left=A(0), middle=D(3), right=U(20)
    Press 1: right U→V  (not yet at notch before this press)   → A D V
    Press 2: right was at notch V → middle D→E; right V→W      → A E W
    Press 3: middle now at notch E → middle E→F + left A→B (double-step!); right W→X
                                                                 → B F X
    """
    m = EnigmaMachine(['I', 'II', 'III'], 'B', start_positions=[0, 3, 20])
    m.encrypt('A')
    assert m.left.position == 0 and m.middle.position == 3 and m.right.position == 21  # A D V

    m.encrypt('A')
    assert m.left.position == 0 and m.middle.position == 4 and m.right.position == 22  # A E W

    m.encrypt('A')   # double-step fires here
    assert m.left.position == 1    # B
    assert m.middle.position == 5  # F
    assert m.right.position == 23  # X


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def test_ioc_english_higher():
    """English text has higher IoC than random-looking text."""
    english = 'THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG' * 3
    random  = 'XKQZWVJYPLMBTHUNIEROASCDFGXKQZWVJY' * 3
    assert index_of_coincidence(english) > index_of_coincidence(random)


def test_chi_squared_english_lower():
    """English text has lower chi-squared than a string of rare letters."""
    english = 'THEANDFORISARE' * 10
    bad     = 'ZQXJKVBPZQXJKV' * 10
    assert chi_squared_score(english) < chi_squared_score(bad)


# ---------------------------------------------------------------------------
# Code breaker (fast subset — three rotors, one reflector, small position space)
# ---------------------------------------------------------------------------

def test_crack_with_crib():
    """Crack a short message using a crib word, searching a small rotor subset."""
    plaintext = 'ATTACKATDAWN'
    m = EnigmaMachine(['I', 'II', 'III'], 'B', start_positions=[0, 3, 14])
    ciphertext = m.encrypt(plaintext)

    results = crack_enigma(
        ciphertext=ciphertext,
        crib='ATTACK',
        use_reflectors=['B'],
        use_rotors=['I', 'II', 'III'],
        top_n=3,
        verbose=False,
    )
    assert results, "Breaker found no candidates"
    assert any('ATTACK' in r['plaintext'] for r in results), \
        "Crib not present in any candidate plaintext"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    ('Known vector AAAAA→BDZGO',         test_known_vector_aaaaa),
    ('Known vector second character',     test_known_vector_b),
    ('Known vector with notch positions', test_known_vector_with_position),
    ('Symmetric encryption',              test_symmetric),
    ('No letter self-encrypts',           test_no_letter_self_encrypts),
    ('Plugboard symmetric',               test_plugboard_symmetric),
    ('Plugboard changes output',          test_plugboard_changes_output),
    ('Ring setting changes output',       test_ring_setting_changes_output),
    ('Different rotors differ',           test_different_rotors_differ),
    ('Reflectors differ',                 test_reflectors_differ),
    ('Non-alpha passthrough',             test_non_alpha_passthrough),
    ('Double-stepping anomaly',           test_double_stepping),
    ('IoC: English > random',             test_ioc_english_higher),
    ('Chi²: English lower than noise',    test_chi_squared_english_lower),
    ('Crack with crib',                   test_crack_with_crib),
]


if __name__ == '__main__':
    print("Enigma Machine Test Suite")
    print("=" * 50)
    passed = sum(run(name, fn) for name, fn in TESTS)
    total = len(TESTS)
    print("=" * 50)
    print(f"{passed}/{total} tests passed.")
    if passed < total:
        raise SystemExit(1)
