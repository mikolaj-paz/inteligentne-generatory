import random
from datetime import datetime
from typing import override
from seeder.generation.base import BaseGenerator


class HireDateGenerator(BaseGenerator):
    name = "data_zatrudnienia"

    @override
    def generate(
        self, context: dict = None, year_from: int = 1960, year_to: int = 2025, **kwargs
    ) -> datetime:
        ctx = context if context is not None else {}

        start_date = datetime(year_from, 1, 1)
        end_date = datetime(year_to, 12, 31)
        hire_date = start_date + (end_date - start_date) * random.random()
        hire_date = hire_date.date()

        ctx["hire_date"] = hire_date

        return hire_date
