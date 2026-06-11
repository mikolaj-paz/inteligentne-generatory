import random
from seeder.generation.base import BaseGenerator

class SalaryGenerator(BaseGenerator):
    name = "wynagrodzenie"

    def generate(self, context: dict = None, **kwargs) -> float:
        salary = random.uniform(4000.0, 42000.0)
        return round(salary, 2)