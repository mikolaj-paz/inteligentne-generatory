from typing import override
import random

from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.checksum import mod11_weighted

_CHECKSUM_WEIGHTS = [8, 9, 2, 3, 4, 5, 6, 7]


class RegonGenerator(BaseGenerator):
    name = "regon"

    @override
    def generate(self) -> str:
        """Generate a random 9-digit REGON (Polish business identification number)."""

        regon = "".join(str(random.randint(0, 9)) for _ in range(8))
        checksum = mod11_weighted(regon, _CHECKSUM_WEIGHTS)

        return regon + str(checksum % 10)
