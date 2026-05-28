import random
from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict


class CompanyNameGenerator(BaseGenerator):
    name = "firma"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        base = fetch_random_from_dict("NazwiskaMeskie", "nazwisko")

        structures = [
            f"P.H.U. {base}",
            f"Zakład Usługowy {base}",
            f"{base} i Synowie",
            f"{base} Group",
            f"{base} Sp. z o.o.",
            f"Przedsiębiorstwo {base}",
            f"Bud-Max {base}",
            f"Trans-{base}",
        ]

        return random.choice(structures)
