import random
from typing import override
from seeder.generation.base import BaseGenerator


class PositionGenerator(BaseGenerator):
    name = "stanowisko"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        positions = [
            "Dyrektor Generalny (CEO)",
            "Dyrektor Operacyjny",
            "Dyrektor Finansowy",
            "Dyrektor ds. Marketingu",
            "Kierownik Działu HR",
            "Specjalista ds. Rekrutacji",
            "Główna Księgowa",
            "Młodszy Księgowy",
            "Kierownik Projektu (Project Manager)",
            "Kierownik Działu Sprzedaży",
            "Specjalista ds. Obsługi Klienta",
            "Przedstawiciel Handlowy",
            "Kierownik Administracji",
            "Asystent Zarządu / Recepcjonista",
            "Specjalista ds. Zaopatrzenia",
            "Koordynator ds. Logistyki",
            "Radca Prawny / Doradca",
            "Praktykant / Stażysta"
        ]

        return random.choice(positions)