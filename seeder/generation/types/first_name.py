from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict, resolve_gender


class FirstNameGenerator(BaseGenerator):
    name = "imie"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        ctx = context if context is not None else {}
        gender = resolve_gender(ctx)

        table = "ImionaMeskie" if gender == "M" else "ImionaZenskie"
        return str(fetch_random_from_dict(table, "imie"))
