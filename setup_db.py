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

    df_terc = pd.read_csv(terc_path, sep=";", dtype=str)

    # =========================================================================
    # 1. WOJEWÓDZTWO
    # =========================================================================
    woj = df_terc[df_terc["POW"].isna() & df_terc["GMI"].isna()][
        ["WOJ", "NAZWA"]
    ].copy()
    woj.columns = ["kod_woj_gus", "nazwa"]
    woj.to_sql("Wojewodztwo", conn, if_exists="replace", index=False)

    woj_map = pd.read_sql(
        "SELECT rowid as id_wojewodztwo, kod_woj_gus FROM Wojewodztwo", conn
    )

    woj_to_db = df_terc[df_terc["POW"].isna() & df_terc["GMI"].isna()][
        ["WOJ", "NAZWA"]
    ].copy()
    woj_to_db.columns = ["kod_woj_gus", "nazwa"]
    woj_to_db = woj_to_db.merge(woj_map, on="kod_woj_gus", how="inner")
    woj_to_db[["id_wojewodztwo", "nazwa"]].to_sql(
        "Wojewodztwo", conn, if_exists="replace", index=False
    )

    # =========================================================================
    # 2. POWIAT
    # =========================================================================
    powiaty = df_terc[df_terc["POW"].notna() & df_terc["GMI"].isna()].copy()
    powiaty["kod_pow_gus"] = powiaty["WOJ"] + powiaty["POW"]
    powiaty = powiaty.rename(columns={"NAZWA": "nazwa", "WOJ": "kod_woj_gus"})

    powiaty = powiaty.merge(woj_map, on="kod_woj_gus", how="inner")
    powiaty.to_sql("Powiat_Temp", conn, if_exists="replace", index=False)

    pow_map = pd.read_sql(
        "SELECT rowid as id_powiat, kod_pow_gus FROM Powiat_Temp", conn
    )
    powiaty = powiaty.merge(pow_map, on="kod_pow_gus", how="inner")

    powiaty_to_db = powiaty[["id_powiat", "nazwa", "id_wojewodztwo"]].copy()
    powiaty_to_db.to_sql("Powiat", conn, if_exists="replace", index=False)

    # =========================================================================
    # 3. GMINA (Tylko unikalne nazwy w powiecie)
    # =========================================================================
    gminy = df_terc[df_terc["GMI"].notna()].copy()

    gminy["kod_pow_gus"] = gminy["WOJ"] + gminy["POW"]
    gminy = gminy.merge(pow_map, on="kod_pow_gus", how="inner")

    gminy["kod_gmi_gus_6"] = gminy["WOJ"] + gminy["POW"] + gminy["GMI"]
    gminy = gminy.rename(columns={"NAZWA": "nazwa"})

    gminy = gminy.drop_duplicates(subset=["nazwa", "id_powiat"])

    gminy.to_sql("Gmina_Temp", conn, if_exists="replace", index=False)

    gmi_map = pd.read_sql(
        "SELECT rowid as id_gmina, kod_gmi_gus_6 as kod_gmi_gus FROM Gmina_Temp", conn
    )
    gminy = gminy.merge(
        gmi_map, left_on="kod_gmi_gus_6", right_on="kod_gmi_gus", how="inner"
    )

    gminy_to_db = gminy[["id_gmina", "nazwa", "id_powiat"]].copy()
    gminy_to_db.to_sql("Gmina", conn, if_exists="replace", index=False)

    # =========================================================================
    # 4. MIEJSCOWOŚĆ (SIMC)
    # =========================================================================
    df_simc = pd.read_csv(simc_path, sep=";", dtype=str)

    df_simc["kod_gmi_gus"] = df_simc["WOJ"] + df_simc["POW"] + df_simc["GMI"]

    miejscowosci = df_simc.rename(
        columns={"SYM": "kod_miejscowosci_gus", "NAZWA": "nazwa"}
    )

    miejscowosci = miejscowosci.merge(gmi_map, on="kod_gmi_gus", how="inner")
    miejscowosci.to_sql("Miejscowosc_Temp", conn, if_exists="replace", index=False)

    miejscowosci_map = pd.read_sql(
        "SELECT rowid as id_miejscowosc, kod_miejscowosci_gus FROM Miejscowosc_Temp",
        conn,
    )
    miejscowosci = miejscowosci.merge(
        miejscowosci_map, on="kod_miejscowosci_gus", how="inner"
    )

    miejscowosci_to_db = miejscowosci[["id_miejscowosc", "nazwa", "id_gmina"]].copy()
    miejscowosci_to_db.to_sql("Miejscowosc", conn, if_exists="replace", index=False)

    # =========================================================================
    # 5. ULICE (ULIC)
    # =========================================================================
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

    df_ulic["nazwa"] = df_ulic.apply(create_full_street_name, axis=1)
    ulice = df_ulic.rename(
        columns={"SYM_UL": "kod_ulicy_gus", "SYM": "kod_miejscowosci_gus"}
    ).copy()

    ulice = ulice.merge(miejscowosci_map, on="kod_miejscowosci_gus", how="inner")
    ulice.to_sql("Ulica_Temp", conn, if_exists="replace", index=False)

    ulice_map = pd.read_sql(
        "SELECT rowid as id_ulica, kod_ulicy_gus, id_miejscowosc FROM Ulica_Temp", conn
    )

    ulice_to_db = ulice_map[["id_ulica", "id_miejscowosc"]].copy()

    ulice_final = ulice[["nazwa", "kod_ulicy_gus", "id_miejscowosc"]].merge(
        ulice_map, on=["kod_ulicy_gus", "id_miejscowosc"], how="inner"
    )

    ulice_to_db = ulice_final[["id_ulica", "nazwa", "id_miejscowosc"]].copy()
    ulice_to_db.to_sql("Ulica", conn, if_exists="replace", index=False)

    cursor = conn.cursor()
    cursor.execute("DROP TABLE Powiat_Temp")
    cursor.execute("DROP TABLE Gmina_Temp")
    cursor.execute("DROP TABLE Miejscowosc_Temp")
    cursor.execute("DROP TABLE Ulica_Temp")
    conn.commit()


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
