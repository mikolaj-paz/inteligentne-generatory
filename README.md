# Inteligentne Generatory

**Inteligentne Generatory** to system służący do generowania przykładowych danych osobowych, adresowych oraz biznesowych. Generator tworzy spójne i realistyczne dane, takie jak imiona, nazwiska, adresy, numery PESEL czy dane firm. Wygenerowane rekordy zachowują zależności pomiędzy encjami, np. miasto należy do poprawnego województwa, adres jest zgodny z danymi TERYT, a zatrudnienie odnosi się do istniejącej osoby i firmy.

---

## Opis projektu

### Konfigurowalne generowanie danych

Dane generowane są na podstawie plików konfiguracyjnych w formacie TOML. Użytkownik definiuje liczbę rekordów oraz pola, które mają zostać wygenerowane.

Przykładowa konfiguracja:

```toml
[Osoba]
rows = 150

fields = [
  "imie",
  "nazwisko",
  "data_urodzenia",
  "pesel",
  "plec"
]
```

### Realistyczne dane osobowe

Generator potrafi tworzyć:

* imiona
* nazwiska
* daty urodzenia
* płeć
* poprawne numery PESEL

### Generowanie danych adresowych

Adresy budowane są na podstawie rzeczywistych danych administracyjnych (TERYT), dzięki czemu zachowana jest zgodność pomiędzy:

* województwami
* powiatami
* gminami
* miejscowościami
* ulicami

### Dane firmowe i zatrudnienie

System umożliwia generowanie:

* firm
* rodzajów umów
* zatrudnienia pracowników
* relacji pomiędzy osobami i firmami

### Spójność danych

Wygenerowane rekordy zachowują logiczne zależności pomiędzy encjami, np.:

* osoba ↔ adres
* pracownik ↔ firma
* miejscowość ↔ gmina ↔ powiat ↔ województwo

### Integracja z SQLite

Dane mogą zostać zapisane bezpośrednio do bazy SQLite.

### Eksport do SQL

Istnieje możliwość wyeksportowania wygenerowanych danych do skryptu SQL.

### Tryb podglądu

Opcja `--dry-run` pozwala sprawdzić poprawność konfiguracji bez zapisywania danych do bazy.

---

## Tech Stack

| Warstwa       | Technologia |
| ------------- | ----------- |
| Język         | Python 3    |
| CLI           | Click       |
| Konfiguracja  | TOML        |
| Baza danych   | SQLite      |
| Źródła danych | CSV, TERYT  |
| Progress bar  | tqdm        |

---

## Wymagania

* Python 3.10 lub nowszy
* pip
* virtualenv (zalecane)

---

## Uruchomienie projektu

### 1. Utworzenie środowiska

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 3. Uruchomienie generatora

```bash
python main.py --config "configs/example_working.toml" --db-path "databases/testy.db"
```

---

## Przykładowy wynik działania

```text
Database schema creation completed.

Seeding data...

TERYT:          150/150
RodzajUmowy:      4/4
Adres:         150/150
Firma:         150/150
Osoba:         150/150
Zatrudnienie:  150/150

Data seeding completed successfully!
```

---

## Dostępne opcje CLI

```bash
python main.py --help
```

### Parametry

| Opcja            | Opis                                               |
| ---------------- | -------------------------------------------------- |
| `--config PATH`  | Ścieżka do pliku konfiguracyjnego TOML (wymagane)  |
| `--db-path TEXT` | Ścieżka do pliku SQLite (domyślnie baza w pamięci) |
| `--dry-run`      | Podgląd konfiguracji bez zapisu do bazy            |
| `--export PATH`  | Eksport wygenerowanych danych do pliku SQL         |
| `--help`         | Wyświetlenie pomocy                                |

---

## Przykłady użycia

### Generowanie danych do SQLite

```bash
python main.py --config "configs/example_working.toml" --db-path "databases/testy.db"
```

### Podgląd konfiguracji

```bash
python main.py --config "configs/example_working.toml"  --dry-run
```

### Eksport do SQL

```bash
python main.py --config "configs/example_working.toml"  --export "generated.sql"
```

---

## Struktura projektu

```text
.
├── configs/                 # Przykładowe konfiguracje TOML
├── data/
│   └── source/              # Słowniki CSV i dane TERYT
├── databases/              # Bazy SQLite
├── seeder/                 # Logika generowania danych
├── main.py                 # Główny punkt wejścia aplikacji
├── setup_db.py             # Tworzenie schematu bazy słownikowej
├── requirements.txt        # Zależności projektu
└── README.md
```

---

## Źródła danych

Projekt wykorzystuje publicznie dostępne dane do generowania realistycznych i spójnych danych testowych.

### Rejestr PESEL

Słowniki imion i nazwisk wykorzystywane przez generator zostały opracowane na podstawie danych pochodzących z rejestru PESEL osób żyjących udostępnianych przez administrację publiczną.

### TERYT

Dane adresowe wykorzystywane przez system pochodzą z Krajowego Rejestru Urzędowego Podziału Terytorialnego Kraju (TERYT).

Dzięki wykorzystaniu danych TERYT generowane adresy zachowują poprawne zależności pomiędzy:

- województwami,
- powiatami,
- gminami,
- miejscowościami,
- ulicami.
