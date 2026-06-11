import random
from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.constants import POLISH_BANKS
from seeder.generation.helpers.db_utils import fetch_random_from_dict


class BankGenerator(BaseGenerator):
    name = "bank"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        bank_data = random.choice(POLISH_BANKS)
        return bank_data["nazwa"]
