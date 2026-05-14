from typing import override
import random
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict


class LastNameGenerator(BaseGenerator):
    name = "nazwisko"

    @override
    def generate(self, **kwargs) -> str:
        gender = kwargs.get('gender')

        if not gender:
            gender = random.choice(['M', 'F'])

        table = "NazwiskaMeskie" if gender == 'M' else "NazwiskaZenskie"
        return str(fetch_random_from_dict(table, "nazwisko"))