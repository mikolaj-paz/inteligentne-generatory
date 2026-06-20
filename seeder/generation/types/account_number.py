from typing import override
import random

from seeder.generation.base import BaseGenerator
from seeder.generation.types.nrb import NrbGenerator
from seeder.generation.helpers.checksum import mod97_nrb


class AccountNumberGenerator(BaseGenerator):
    name = "numer_konta"

    def _checksum(self, account_number: str) -> str:
        return mod97_nrb(account_number)

    @override
    def generate(self, context: dict = None, **kwargs) -> str:
        ctx = context if context is not None else {}
        row_data = ctx.get("row_data", {})
        bank_cache = ctx.get("bank_cache", {})

        bank_id = row_data.get("id_bank") or row_data.get("bank_id")

        nrb = bank_cache.get(bank_id)

        if not nrb:
            nrb_gen = NrbGenerator()
            nrb = nrb_gen.generate(context=context)

        if len(nrb) == 8:
            core_bank_code = nrb
        else:
            core_bank_code = nrb[-8:] if len(nrb) >= 8 else nrb.zfill(8)

        customer_digits = "".join(str(random.randint(0, 9)) for _ in range(16))

        account_without_checksum = core_bank_code + customer_digits
        checksum = self._checksum(account_without_checksum)

        return checksum + account_without_checksum