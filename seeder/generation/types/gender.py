import random
from typing import override
from seeder.generation.base import BaseGenerator


class GenderGenerator(BaseGenerator):
    name = "plec"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        ctx = context if context is not None else {}

        existing_gender = ctx.get("gender")

        if existing_gender:
            if hasattr(existing_gender, "value"):
                return str(existing_gender.value)
            return str(existing_gender)

        gender = random.choice(["M", "F"])
        ctx["gender"] = gender

        return gender
