import random
from typing import override
from seeder.generation.base import BaseGenerator

class GenderGenerator(BaseGenerator):
    name = "plec"

    @override
    def generate(self, **kwargs) -> str:
        return random.choice(["M", "F"])