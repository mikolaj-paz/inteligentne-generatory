import time
from datetime import date

from seeder.generation.types.pesel import PeselGenerator


def test_pesel_uniqueness():
    print("🚀 Rozpoczynam test unikalności generatora PESEL...")

    generator = PeselGenerator()

    table_context = {
        "used_pesels": set(),
        "gender": "M",
        "birth_date": date(1995, 5, 5)
    }

    sample = 4500

    print(f"-> Próba wygenerowania {sample} PESEL-i dla dokładnie tej samej daty i płci...")

    start_time = time.time()

    wygenerowane_pesele = []
    for _ in range(sample):
        row_context = {
            "used_pesels": table_context["used_pesels"],
            "gender": table_context["gender"],
            "birth_date": table_context["birth_date"]
        }

        pesel = generator.generate(context=row_context)
        wygenerowane_pesele.append(pesel)

    end_time = time.time()

    liczba_wygenerowanych = len(wygenerowane_pesele)
    liczba_unikalnych = len(set(wygenerowane_pesele))

    print("\n--- WYNIKI TESTU ---")
    print(f"Wygenerowano łącznie: {liczba_wygenerowanych} rekordów.")
    print(f"Liczba unikalnych w zbiorze: {liczba_unikalnych}.")
    print(f"Czas wykonania: {end_time - start_time:.4f} sekundy.")

    if liczba_wygenerowanych == liczba_unikalnych:
        print("\n✅ Sukces! Generator nie stworzył ani jednego duplikatu.")
    else:
        print("\n❌ Błąd! W paczce danych pojawiły się duplikaty.")

    print("\nPrzykładowe wygenerowane numery:")
    for p in wygenerowane_pesele[:5]:
        print(f"  - {p}")


if __name__ == "__main__":
    test_pesel_uniqueness()