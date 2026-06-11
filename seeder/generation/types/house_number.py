import random
from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict, resolve_gender


class HouseNumberGenerator(BaseGenerator):
    name = "numer_domu"

    @override
    def generate(self, context: dict = None, **kwargs) -> int:
        return random.randint(1, 200)
