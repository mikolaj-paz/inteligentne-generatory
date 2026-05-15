from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict

class VoivodeshipGenerator(BaseGenerator):
    name = "wojewodztwo"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        return str(fetch_random_from_dict("Wojewodztwo", "Nazwa"))