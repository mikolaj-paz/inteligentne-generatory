from typing import override
import random

from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.constants import POLISH_BANKS

BANK_CODE_TO_NAME = {
    101: "Narodowy Bank Polski",
    102: "Powszechna Kasa Oszczędności Bank Polski SA",
    105: "ING Bank Śląski SA",
    109: "Bank Zachodni WBK SA",
    160: "BNP PARIBAS BANK POLSKA SA",
    191: "Deutsche Bank Polska S.A",
    194: "Credit Agricole Bank Polska S.A.",
    215: "mBank Hipoteczny SA",
}

_CHECKSUM_WEIGHTS = [3, 9, 7, 1, 3, 9, 7]


class NrbGenerator(BaseGenerator):
    name = "nrb"

    def _institution_code(self, bank_name: str) -> str:
        """Generate a random 4-digit institution code based on the provided bank codes."""
        bank_map = {b["nazwa"]: b["kod_rozliczeniowy"] for b in POLISH_BANKS}
        institution_code = bank_map.get(bank_name)
        return institution_code

    def _department_code(self) -> str:
        return str(random.randint(1, 999)).zfill(3)

    def _checksum(self, nrb_without_checksum: str) -> str:
        weighted_sum = sum(
            digit * weight
            for digit, weight in zip(map(int, nrb_without_checksum), _CHECKSUM_WEIGHTS)
        )
        return str((10 - (weighted_sum % 10)) % 10)

    @override
    def generate(
        self,
        bank_code_to_name: dict[int, str] = BANK_CODE_TO_NAME,
        context: dict = None,
        **kwargs
    ) -> str:
        """Generate a random 8-digit NRB (Polish bank number)."""
        ctx = context if context is not None else {}
        name = ctx["row_data"]['nazwa']
        nrb_without_checksum = (
            self._institution_code(name) + self._department_code()
        )
        return nrb_without_checksum + self._checksum(nrb_without_checksum)
