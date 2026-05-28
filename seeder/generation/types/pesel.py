import random
from datetime import datetime
from enum import Enum
from typing import override

from seeder.generation.base import BaseGenerator


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

    def _generate_birth_date_part(self, birth_date: datetime) -> str:
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

        gender_val = ctx.get("gender")
        if not gender_val:
            gender_enum = random.choice([Gender.MALE, Gender.FEMALE])
            ctx["gender"] = gender_enum.value
        else:
            gender_enum = (
                Gender.MALE
                if str(gender_val).upper() in ["M", "MALE"]
                else Gender.FEMALE
            )

        birth_date_obj = ctx.get("birth_date")

        if not birth_date_obj:
            start_date = datetime(year_from, 1, 1)
            end_date = datetime(year_to, 12, 31)
            birth_date_obj = start_date + (end_date - start_date) * random.random()
            ctx["birth_date"] = birth_date_obj.date()

        birth_date_part = self._generate_birth_date_part(birth_date_obj)
        gender_digit = self._generate_gender_digit(gender_enum)

        while True:
            serial_number = f"{random.randint(0, 999):03d}"
            without_checksum = birth_date_part + serial_number + gender_digit

            checksum = self._generate_checksum(without_checksum)

            # TODO Ensure PESEL is unique in database
            return without_checksum + str(checksum)
