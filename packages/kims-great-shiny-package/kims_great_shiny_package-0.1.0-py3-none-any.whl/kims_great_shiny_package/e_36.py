from freedonia import DATA


def calculate_tax(amount: float, state: str, hour: int):
    return amount + ((amount * DATA[state]) * (hour / 24))