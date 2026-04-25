from typing import override

from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.checksum import mod11_weighted
import random

_CHECKSUM_WEIGHTS = [6, 5, 7, 2, 3, 4, 5, 6, 7]


class NipGenerator(BaseGenerator):
    name = "nip"

    def _generate_prefix(self) -> str:
        """Generate the first 3 digits of the NIP number."""

        return str(random.randint(10, 99) * 10 + random.randint(1, 9))

    @override
    def generate(self) -> str:
        """Generate a random 10-digit NIP (Polish tax identification number)."""

        while True:
            prefix = self._generate_prefix()
            sequential_digits = "".join(str(random.randint(0, 9)) for _ in range(6))

            checksum = mod11_weighted(prefix + sequential_digits, _CHECKSUM_WEIGHTS)

            if checksum < 10:
                break

        return prefix + sequential_digits + str(checksum)
