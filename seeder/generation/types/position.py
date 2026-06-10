import random
from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.constants import INDUSTRY_POSITIONS


class PositionGenerator(BaseGenerator):
    name = "stanowisko"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        row_data = context["row_data"]
        company_cache = context["company_cache"]
        print(company_cache, row_data["id_firma"])

        firma_id = row_data.get("id_firma")

        if firma_id is None:
            industry = random.choice(list(INDUSTRY_POSITIONS.keys()))
        else:
            industry = company_cache.get(firma_id)

            if industry is None:
                industry = random.choice(list(INDUSTRY_POSITIONS.keys()))

        positions = INDUSTRY_POSITIONS[industry]

        return random.choice(positions)