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

    def _generate_birth_date_part(self, year_from: int, year_to: int) -> str:
        """Generate the birth date part of the PESEL number."""

        start_date = datetime(year_from, 1, 1)
        end_date = datetime(year_to, 12, 31)
        random_date = start_date + (end_date - start_date) * random.random()

        year = random_date.year % 100
        month = random_date.month + _CENTURY_MONTH_OFFSETS[random_date.year // 100]
        day = random_date.day

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
        self, year_from: int = 1950, year_to: int = 2005, gender: Gender = "F"
    ) -> str:
        """Generate a random 11-digit PESEL (Polish national identification number)."""

        birth_date = self._generate_birth_date_part(year_from, year_to)
        gender_digit = self._generate_gender_digit(gender)

        while True:
            serial_number = f"{random.randint(0, 999):03d}"
            without_checksum = birth_date + serial_number + gender_digit

            checksum = self._generate_checksum(without_checksum)

            # TODO Ensure PESEL is unique in database
            return without_checksum + str(checksum)
