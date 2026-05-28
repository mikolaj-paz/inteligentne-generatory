from typing import override
import random
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict


class FirstNameGenerator(BaseGenerator):
    name = "imie"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        ctx = context if context is not None else {}
        gender = ctx.get("gender")

        if not gender:
            gender = random.choice(["M", "F"])
            ctx["gender"] = gender

        table = "ImionaMeskie" if gender == "M" else "ImionaZenskie"
        return str(fetch_random_from_dict(table, "imie"))
