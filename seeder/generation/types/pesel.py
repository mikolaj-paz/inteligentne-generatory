import random
from datetime import date
from enum import Enum
from typing import override

from seeder.generation.base import BaseGenerator
from seeder.generation.helpers.db_utils import resolve_gender
from seeder.generation.types.birth_date import BirthDateGenerator


class Gender(Enum):
    MALE = "M"
    FEMALE = "F"


_CENTURY_MONTH_OFFSETS = {
    18: 80,
    19: 0,
    20: 20,
    21: 40,
    22: 60,
}

_CHECKSUM_WEIGHTS = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]


class PeselGenerator(BaseGenerator):
    name = "pesel"

    def _generate_checksum(self, digits: str) -> int:
        """Calculate the checksum digit for the PESEL number."""
        weighted_sum = sum(
            (digit * weight) % 10
            for digit, weight in zip(map(int, digits), _CHECKSUM_WEIGHTS)
        )
        return (10 - weighted_sum % 10) % 10

    def _generate_birth_date_part(self, birth_date: date) -> str:
        """Generate the birthdate part of the PESEL number."""

        year = birth_date.year % 100
        month = birth_date.month + _CENTURY_MONTH_OFFSETS[birth_date.year // 100]
        day = birth_date.day

        return f"{year:02d}{month:02d}{day:02d}"

    def _generate_gender_digit(self, gender: Gender) -> str:
        """Generate the gender digit of the PESEL number."""

        match gender:
            case Gender.MALE:
                choices = [1, 3, 5, 7, 9]
            case Gender.FEMALE:
                choices = [0, 2, 4, 6, 8]
            case _:
                raise ValueError("Invalid gender specified. Must be 'M' or 'F'.")

        return str(random.choice(choices))

    @override
    def generate(
        self, context: dict = None, year_from: int = 1950, year_to: int = 2005, **kwargs
    ) -> str:
        """Generate a random 11-digit PESEL (Polish national identification number)."""

        ctx = context if context is not None else {}

        if "used_pesels" not in ctx:
            ctx["used_pesels"] = set()
        used_pesels = ctx["used_pesels"]

        gender_str = resolve_gender(ctx)
        gender_enum = Gender.MALE if gender_str == "M" else Gender.FEMALE

        birth_date_obj = BirthDateGenerator().generate(
            ctx, year_from=year_from, year_to=year_to
        )

        birth_date_part = self._generate_birth_date_part(birth_date_obj)
        gender_digit = self._generate_gender_digit(gender_enum)

        while True:
            serial_number = f"{random.randint(0, 999):03d}"
            without_checksum = birth_date_part + serial_number + gender_digit

            checksum = self._generate_checksum(without_checksum)

            full_pesel = without_checksum + str(checksum)
            if full_pesel not in used_pesels:
                used_pesels.add(full_pesel)
                return full_pesel
