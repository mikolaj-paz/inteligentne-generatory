from collections.abc import Sequence


def mod11_weighted(digits: str, weights: Sequence[int]) -> int:
    if len(digits) != len(weights):
        raise ValueError("Digits and weights must be of the same length")

    return sum(digit * weight for digit, weight in zip(map(int, digits), weights)) % 11


def mod97_iban(bban: str, country_code: str = "PL") -> str:
    cleaned_bban = bban.replace(" ", "")
    if not cleaned_bban.isdigit():
        raise ValueError("BBAN must contain only digits")

    cc = country_code.upper()
    if len(cc) != 2 or not cc.isalpha():
        raise ValueError("Country code must be two letters")

    rearranged = f"{cleaned_bban}{cc}00"
    numeric = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in rearranged)

    remainder = 0
    for ch in numeric:
        remainder = (remainder * 10 + int(ch)) % 97

    check_digits = 98 - remainder
    return f"{check_digits:02d}"
