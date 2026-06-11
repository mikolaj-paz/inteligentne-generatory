from black.trans import defaultdict
from seeder.generation.types.company_name import CompanyNameGenerator


def run_test():
    gen = CompanyNameGenerator()

    results = []
    industry_counter = defaultdict(int)

    print("\n--- GENERATED COMPANIES ---\n")

    for i in range(100):
        row_data = {}
        name = gen.generate(context={"row_data": row_data})

        industry = row_data.get("industry")

        results.append(name)
        industry_counter[industry] += 1

        print(f"{i+1:03d}. [{industry}] {name}")

    print("\n--- SUMMARY ---")
    print("Total:", len(results))
    print("Unique:", len(set(results)))

    print("\n--- INDUSTRY DISTRIBUTION ---")
    for ind, count in sorted(industry_counter.items(), key=lambda x: -x[1]):
        print(f"{ind}: {count}")


if __name__ == "__main__":
    run_test()
