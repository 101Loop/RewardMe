import random
import string


def random_number_token(length=6):
    """
    Returns a string of random digits encoded as string.
    :param int length: The number of digits to return.
    :returns: A string of decimal digits.
    :rtype: str
    """
    rand = random.SystemRandom()

    if hasattr(rand, "choices"):
        digits = rand.choices(string.digits, k=length)
    else:
        digits = (rand.choice(string.digits) for _ in range(length))

    return "".join(digits)
