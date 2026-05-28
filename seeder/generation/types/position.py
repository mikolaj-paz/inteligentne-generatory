import random
from typing import override
from seeder.generation.base import BaseGenerator


class PositionGenerator(BaseGenerator):
    name = "stanowisko"

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        positions = [
            "Lekarz internista", "Lekarz rezydent", "Lekarz pediatra",
            "Dentysta / Stomatolog", "Chirurg szczękowy", "Lekarz weterynarii",
            "Pielęgniarka oddziałowa", "Fizjoterapeuta", "Ratownik medyczny",

            "Nauczyciel mianowany", "Nauczyciel dyplomowany", "Wychowawca świetlicy",
            "Wykładowca akademicki", "Profesor uczelni", "Asystent naukowo-dydaktyczny",

            "Młodszy programista (Junior Python Developer)", "Starszy programista",
            "Analityk danych", "Kierownik projektu (Project Manager)",
            "Specjalista ds. HR", "Główna księgowa", "Przedstawiciel handlowy",
            "Dyrektor finansowy", "Recepcjonista / Asystent biura",

            "Kierownik magazynu", "Pracownik logistyki", "Kurier",
            "Sprzedawca / Doradca klienta", "Kierownik sklepu", "Szef kuchni"
        ]
        return random.choice(positions)