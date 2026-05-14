from typing import override
import random
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict


class LastNameGenerator(BaseGenerator):
    name = "imie"

    @override
    def generate(self, **kwargs) -> str:
        gender = kwargs.get('gender')

        if not gender:
            gender = random.choice(['M', 'F'])

        table = "ImionaMeskie" if gender == 'M' else "ImionaZenskie"
        return str(fetch_random_from_dict(table, "imie"))