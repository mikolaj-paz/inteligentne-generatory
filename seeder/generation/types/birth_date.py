import random
from datetime import datetime
from typing import override
from seeder.generation.base import BaseGenerator


class BirthDateGenerator(BaseGenerator):
    name = "data_urodzenia"

    @override
    def generate(self, context: dict = None, year_from: int = 1950, year_to: int = 2005, **kwargs) -> datetime:
        ctx = context if context is not None else {}

        birth_date = ctx.get('birth_date')

        if not birth_date:
            start_date = datetime(year_from, 1, 1)
            end_date = datetime(year_to, 12, 31)
            birth_date = start_date + (end_date - start_date) * random.random()
            birth_date = birth_date.date()

            ctx['birth_date'] = birth_date

        return birth_date