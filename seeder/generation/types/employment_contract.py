from typing import override
import random

from seeder.generation.base import BaseGenerator


class EmploymentContractGenerator(BaseGenerator):
    name = "rodzajumowy"

    _CONTRACT_TYPES = [
        "Umowa o pracę",
        "Umowa o dzieło",
        "Umowa zlecenie",
        "Kontrakt B2B"
    ]

    _global_index = 0

    @override
    def generate(
            self,
            context: dict | None = None,
    ) -> str:
        """Generate a random Polish employment contract type."""
        contract = self._CONTRACT_TYPES[EmploymentContractGenerator._global_index % len(self._CONTRACT_TYPES)]
        EmploymentContractGenerator._global_index += 1

        return contract