import random
import string


def password_generator(
    uppercase_count: int = 0,
    lowercase_count: int = 0,
    numeric_count: int = 0,
    punctuation_count: int = 0,
    exclude: str = "",
):
    password_list = []
    if uppercase_count:
        password_list.extend(
            _random_list(
                amount=uppercase_count,
                choices=string.ascii_uppercase,
                exclude=exclude,
            )
        )
    if lowercase_count:
        password_list.extend(
            _random_list(
                amount=lowercase_count,
                choices=string.ascii_lowercase,
                exclude=exclude,
            )
        )
    if numeric_count:
        password_list.extend(
            _random_list(
                amount=numeric_count,
                choices=string.digits,
                exclude=exclude,
            )
        )
    if punctuation_count:
        password_list.extend(
            _random_list(
                amount=punctuation_count,
                choices=string.punctuation,
                exclude=exclude,
            )
        )

    random.shuffle(password_list)
    return "".join(password_list)


def _random_list(amount: int, choices: str, exclude: str = "") -> list:
    result = []
    i = 0
    while i < amount:
        tmp = random.choice(choices)
        if tmp not in exclude:
            result.append(tmp)
            i += 1
    return result
