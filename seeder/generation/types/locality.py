from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict

class LocalityGenerator(BaseGenerator):
    name = "miejscowosc"

    @override
    def generate(self, **kwargs) -> str:
        return str(fetch_random_from_dict("Miejscowosc", "Nazwa"))