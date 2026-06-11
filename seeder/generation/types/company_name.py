import random
from typing import override
from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import fetch_random_from_dict
from seeder.generation.helpers.constants import INDUSTRY, INDUSTRY_PATTERNS


class CompanyNameGenerator(BaseGenerator):
    name = "firma"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        row_data = context.get("row_data")
        industry = random.choice(INDUSTRY)
        row_data["_industry"] = industry

        industry_data = INDUSTRY_PATTERNS[industry]
        template = random.choice(industry_data["templates"])

        format_kwargs = {}
        for key, words in industry_data.items():
            if key != "templates" and f"{{{key}}}" in template:
                format_kwargs[key] = random.choice(words)

        return template.format(**format_kwargs)
