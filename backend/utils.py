def generate_random_string(length: int = 10) -> str:
    import random
    import string

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
