import random
from seeder.generation.base import BaseGenerator


class BalanceGenerator(BaseGenerator):
    name = "saldo"

    def generate(self, context: dict = None, **kwargs) -> float:
        balance = random.uniform(-100.0, 50000.0)
        return round(balance, 2)
