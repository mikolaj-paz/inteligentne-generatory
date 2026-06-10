import random

from seeder.generation.types.company_name import CompanyNameGenerator
from seeder.generation.types.position import PositionGenerator
from seeder.generation.helpers.constants import INDUSTRY, INDUSTRY_POSITIONS


def run_test(n=100):
    company_gen = CompanyNameGenerator()
    position_gen = PositionGenerator()

    company_cache = {}
    results = []

    # 1. generujemy firmy
    for company_id in range(1, n + 1):
        row_data = {}

        company_name = company_gen.generate(context={"row_data": row_data})

        industry = row_data["_industry"]
        company_cache[company_id] = industry

        results.append({
            "company_id": company_id,
            "company": company_name,
            "industry": industry
        })

    # 2. generujemy zatrudnienia
    print("\n=== EMPLOYMENT TEST ===\n")

    for company_id in range(1, n + 1):
        row_data = {
            "firma_id": company_id
        }

        context = {
            "row_data": row_data,
            "company_cache": company_cache
        }

        position = position_gen.generate(context)

        industry = company_cache[company_id]
        allowed_positions = INDUSTRY_POSITIONS[industry]

        print(f"Firma {company_id} ({industry}) -> {position}")

        assert position in allowed_positions, (
            f"BŁĄD: {position} nie pasuje do {industry}"
        )

    print("\nOK: wszystkie stanowiska zgodne z branżami")


if __name__ == "__main__":
    run_test(100)