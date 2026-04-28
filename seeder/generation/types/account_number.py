from typing import override
import random

from seeder.generation.base import BaseGenerator
from seeder.generation.types.nrb import NrbGenerator
from seeder.generation.helpers.checksum import mod97_nrb


class AccountNumberGenerator(BaseGenerator):
    name = "account_number"

    def _checksum(self, account_number: str) -> str:
        return mod97_nrb(account_number)

    @override
    def generate(self) -> str:
        """Generate a random 26-digit bank account number (numer rachunku)."""
        nrb_gen = NrbGenerator()
        nrb = nrb_gen.generate()
        account_number = nrb + "".join(str(random.randint(0, 9)) for _ in range(16))
        checksum = self._checksum(account_number)
        return checksum + account_number
