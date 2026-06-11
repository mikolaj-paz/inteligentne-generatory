import random
from typing import override
from seeder.generation.base import BaseGenerator


class FlatNumber(BaseGenerator):
    name = "numer_mieszkania"

    @override
    def generate(self, context: dict = None, **kwargs) -> int | None:
        if random.random() < 0.4:
            return None

        return random.randint(1, 100)
