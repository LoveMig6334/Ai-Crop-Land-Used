def calculate_price(corp: str, cycle: list, price: list) -> float:
    total = 0.0
    for i in cycle:
        total += price[i]

    return total
