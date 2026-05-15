"""
Enigma Machine Simulator

Simulates the German WWII Enigma cipher machine used for encrypted communications.
Supports Army/Luftwaffe rotors I-V, reflectors UKW-B and UKW-C, ring settings,
start positions, and plugboard (Steckerbrett) pairs.

The Enigma machine is symmetric: encrypting a ciphertext with the same settings
used to encrypt the plaintext recovers the original plaintext.
"""

from typing import List, Optional

# Rotor wiring and notch positions (letter at which this rotor steps the next rotor)
# Notch position is stored as an integer (A=0, B=1, ..., Z=25)
ROTOR_DATA = {
    'I':   ('EKMFLGDQVZNTOWYHXUSPAIBRCJ', 16),  # notch at Q
    'II':  ('AJDKSIRUXBLHWTMCQGZNPYFVOE',  4),  # notch at E
    'III': ('BDFHJLCPRTXVZNYEIWGAKMUSQO', 21),  # notch at V
    'IV':  ('ESOVPZJAYQUIRHXLNFTGKDCMWB',  9),  # notch at J
    'V':   ('VZBRGITYUPSDNHLXAWMJQOFECK', 25),  # notch at Z
}

REFLECTOR_DATA = {
    'B': 'YRUHQSLDPXNGOKMIEBFZCWVJAT',
    'C': 'FVPJIAOYEDRZXWGCTKUQSBNMHL',
}


class Rotor:
    def __init__(self, name: str, ring_setting: int = 0, position: int = 0):
        wiring_str, self.notch = ROTOR_DATA[name]
        self.name = name
        self.ring_setting = ring_setting
        self.position = position
        self.forward_wiring = [ord(c) - 65 for c in wiring_str]
        self.backward_wiring = [0] * 26
        for i, v in enumerate(self.forward_wiring):
            self.backward_wiring[v] = i

    def at_notch(self) -> bool:
        return self.position == self.notch

    def step(self):
        self.position = (self.position + 1) % 26

    def forward(self, signal: int) -> int:
        shift = (self.position - self.ring_setting) % 26
        return (self.forward_wiring[(signal + shift) % 26] - shift) % 26

    def backward(self, signal: int) -> int:
        shift = (self.position - self.ring_setting) % 26
        return (self.backward_wiring[(signal + shift) % 26] - shift) % 26


class Reflector:
    def __init__(self, name: str):
        self.name = name
        self.wiring = [ord(c) - 65 for c in REFLECTOR_DATA[name]]

    def reflect(self, signal: int) -> int:
        return self.wiring[signal]


class Plugboard:
    def __init__(self, pairs: Optional[List[str]] = None):
        self.wiring = list(range(26))
        if pairs:
            for pair in pairs:
                pair = pair.upper()
                a, b = ord(pair[0]) - 65, ord(pair[1]) - 65
                self.wiring[a] = b
                self.wiring[b] = a

    def swap(self, signal: int) -> int:
        return self.wiring[signal]


class EnigmaMachine:
    """
    Full Enigma machine with plugboard, three rotors, and a reflector.

    Rotor names are specified left to right (left=slow, right=fast).
    Positions and ring settings are integers 0-25 (A=0, Z=25).
    """

    def __init__(
        self,
        rotor_names: List[str],
        reflector_name: str = 'B',
        ring_settings: Optional[List[int]] = None,
        start_positions: Optional[List[int]] = None,
        plugboard_pairs: Optional[List[str]] = None,
    ):
        if ring_settings is None:
            ring_settings = [0, 0, 0]
        if start_positions is None:
            start_positions = [0, 0, 0]

        self.left   = Rotor(rotor_names[0], ring_settings[0], start_positions[0])
        self.middle = Rotor(rotor_names[1], ring_settings[1], start_positions[1])
        self.right  = Rotor(rotor_names[2], ring_settings[2], start_positions[2])
        self.reflector = Reflector(reflector_name)
        self.plugboard = Plugboard(plugboard_pairs)

    def _step_rotors(self):
        # Double-stepping anomaly: middle steps alongside left when at its own notch
        if self.middle.at_notch():
            self.middle.step()
            self.left.step()
        elif self.right.at_notch():
            self.middle.step()
        self.right.step()

    def encrypt_char(self, char: str) -> str:
        if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            return char

        self._step_rotors()

        signal = ord(char) - 65
        signal = self.plugboard.swap(signal)
        signal = self.right.forward(signal)
        signal = self.middle.forward(signal)
        signal = self.left.forward(signal)
        signal = self.reflector.reflect(signal)
        signal = self.left.backward(signal)
        signal = self.middle.backward(signal)
        signal = self.right.backward(signal)
        signal = self.plugboard.swap(signal)

        return chr(signal + 65)

    def encrypt(self, text: str) -> str:
        """Encrypt or decrypt a message (Enigma is symmetric)."""
        return ''.join(self.encrypt_char(c) for c in text.upper() if c.isalpha())
