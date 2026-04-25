from typing import override
import random

from seeder.generation.base import BaseGenerator


class NrbGenerator(BaseGenerator):
    name = "nrb"

    @override
    def generate(self) -> str:
        """Generate a random 8-digit NRB (Polish bank account number)."""
        nrb = "".join(str(random.randint(0, 9)) for _ in range(26))
        return nrb
