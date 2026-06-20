import random
from datetime import datetime, date
from typing import override
from seeder.generation.base import BaseGenerator


class HireDateGenerator(BaseGenerator):
    name = "data_zatrudnienia"

    @override
    def generate(
        self, context: dict = None, year_from: int = 1960, year_to: int = 2025, **kwargs
    ) -> date:
        ctx = context if context is not None else {}
        row_data = ctx.get("row_data", {})
        birth_date_cache = ctx.get("birth_date_cache", {})

        id_osoba = row_data.get("id_osoba")
        birth_date = birth_date_cache[id_osoba]

        birth_year = birth_date.year
        min_employment_year = birth_year + 18

        if min_employment_year > year_from:
            year_from = min_employment_year

        if year_from > year_to:
            year_to = year_from

        start_date = datetime(year_from, 1, 1)
        end_date = datetime(year_to, 12, 31)
        hire_date = start_date + (end_date - start_date) * random.random()
        hire_date = hire_date.date()

        ctx["hire_date"] = hire_date

        return hire_date
