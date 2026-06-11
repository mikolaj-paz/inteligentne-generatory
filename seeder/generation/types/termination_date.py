import random
from datetime import datetime, timedelta
from typing import override
from seeder.generation.base import BaseGenerator


class TerminationDateGenerator(BaseGenerator):
    name = "data_zwolnienia"

    @override
    def generate(
        self, context: dict | None = None, **kwargs
    ) -> datetime | None:
        ctx = context if context is not None else {}

        if random.random() < 0.7:
            return None

        hire_date = ctx["hire_date"]

        max_days = (datetime.now().date() - hire_date).days

        if max_days <= 1:
            return datetime.now().date()

        return hire_date + timedelta(days=random.randint(1, max_days))
