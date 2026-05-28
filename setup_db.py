import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_DICT_DB = os.path.join(BASE_DIR, "databases", "dictionary.db")
PATH_TARGET_DB = os.path.join(BASE_DIR, "databases", "target.db")
SOURCE_DATA_DIR = os.path.join(BASE_DIR, "data", "source")


def process_personal_data(conn):
    files = {
        "ImionaMeskie": "imiona_meskie.csv",
        "ImionaZenskie": "imiona_zenskie.csv",
        "NazwiskaMeskie": "nazwiska_meskie.csv",
        "NazwiskaZenskie": "nazwiska_zenskie.csv",
    }

    for table, filename in files.items():
        path = os.path.join(SOURCE_DATA_DIR, filename)
        try:
            df = pd.read_csv(path)

            if "imiona" in filename:
                df = df[["IMIĘ_PIERWSZE", "LICZBA_WYSTĄPIEŃ"]]
                df.columns = ["imie", "liczba"]
                df = df.head(240)
            elif "nazwiska" in filename:
                df = df[["Nazwisko aktualne", "Liczba"]]
                df.columns = ["nazwisko", "liczba"]
                df = df.head(23300)

            df.to_sql(table, conn, if_exists="replace", index=False)

        except FileNotFoundError:
            raise FileNotFoundError(f"Brak pliku danych osobowych: {filename}")
        except KeyError as e:
            raise KeyError(f"Nieprawidłowa struktura kolumn w pliku {filename}: {e}")


def process_teryt(conn):
    terc_path = os.path.join(SOURCE_DATA_DIR, "TERC.csv")
    simc_path = os.path.join(SOURCE_DATA_DIR, "SIMC.csv")
    ulic_path = os.path.join(SOURCE_DATA_DIR, "ULIC.csv")

    if not os.path.exists(terc_path) or not os.path.exists(simc_path):
        raise FileNotFoundError("Brak plików TERC.csv lub SIMC.csv w data/source!")

    # 1. TERC
    df_terc = pd.read_csv(terc_path, sep=";", dtype=str)

    # 1.1. WOJEWÓDZTWO
    woj = df_terc[df_terc["POW"].isna() & df_terc["GMI"].isna()][
        ["WOJ", "NAZWA"]
    ].copy()
    woj.columns = ["ID_Wojewodztwo", "Nazwa"]
    woj.to_sql("Wojewodztwo", conn, if_exists="replace", index=False)

    # 1.2. POWIAT
    powiaty = df_terc[df_terc["POW"].notna() & df_terc["GMI"].isna()].copy()
    powiaty["ID_Powiat"] = powiaty["WOJ"] + powiaty["POW"]
    powiaty = powiaty.rename(columns={"NAZWA": "Nazwa", "WOJ": "ID_Wojewodztwo"})
    powiaty = powiaty[["ID_Powiat", "Nazwa", "ID_Wojewodztwo"]]
    powiaty.to_sql("Powiat", conn, if_exists="replace", index=False)

    # 1.3. GMINA
    gminy = df_terc[df_terc["GMI"].notna()].copy()
    gminy["ID_Gmina"] = gminy["WOJ"] + gminy["POW"] + gminy["GMI"]
    gminy["ID_Powiat"] = gminy["WOJ"] + gminy["POW"]

    gminy = gminy.rename(columns={"NAZWA": "Nazwa"})
    gminy = gminy[["ID_Gmina", "Nazwa", "ID_Powiat"]]
    gminy.to_sql("Gmina", conn, if_exists="replace", index=False)

    # 2. MIEJSCOWOŚĆ (SIMC)
    df_simc = pd.read_csv(simc_path, sep=";", dtype=str)
    df_simc["ID_Gmina"] = df_simc["WOJ"] + df_simc["POW"] + df_simc["GMI"]
    miejscowosci = df_simc.rename(columns={"SYM": "ID_Miejscowosc", "NAZWA": "Nazwa"})
    miejscowosci = miejscowosci[["ID_Miejscowosc", "Nazwa", "ID_Gmina"]]
    miejscowosci.to_sql("Miejscowosc", conn, if_exists="replace", index=False)

    # 3. ULICE (ULIC)
    df_ulic = pd.read_csv(ulic_path, sep=";", dtype=str)

    df_ulic.columns = df_ulic.columns.str.strip()

    df_ulic["CECHA"] = df_ulic["CECHA"].fillna("").str.strip()
    df_ulic["NAZWA_1"] = df_ulic["NAZWA_1"].fillna("").str.strip()
    df_ulic["NAZWA_2"] = df_ulic["NAZWA_2"].fillna("").str.strip()

    def create_full_street_name(row):
        parts = [row["CECHA"]]
        if row["NAZWA_2"]:
            parts.append(row["NAZWA_2"])
        parts.append(row["NAZWA_1"])
        return " ".join(parts).strip()

    df_ulic["Nazwa"] = df_ulic.apply(create_full_street_name, axis=1)

    ulice = df_ulic.rename(
        columns={"SYM_UL": "ID_Ulica", "SYM": "ID_Miejscowosc"}
    ).copy()
    ulice = ulice[["ID_Ulica", "Nazwa", "ID_Miejscowosc"]]

    ulice.to_sql("Ulica", conn, if_exists="replace", index=False)


def setup_dictionary_database():
    os.makedirs(os.path.dirname(PATH_DICT_DB), exist_ok=True)

    with sqlite3.connect(PATH_DICT_DB) as conn:
        process_personal_data(conn)
        process_teryt(conn)


def setup_target():
    sql_file_path = os.path.join(BASE_DIR, "schema.sql")

    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"Brak pliku schema.sql w {BASE_DIR}")

    with sqlite3.connect(PATH_TARGET_DB) as conn:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())


if __name__ == "__main__":
    setup_dictionary_database()
    # setup_target()
