def less_divide(lst: tuple) -> float:
    """
    Calculate the less divide of a tuple of numbers.

    Args:
        lst (tuple): A tuple of numbers.
        Returns:
        float: The result of the less divide operation.

    Example:
        >>> less_divide((10, 2, 5))
        1.0
    """

    result = lst[0]
    for num in lst[1:]:
        if num == 0:
            raise ValueError("Division by zero is not allowed.")
        result /= num
    return result


def price_ratio(p_dict: dict) -> dict:
    sum = 0

    for key, value in p_dict.items():
        if value == 0:
            raise ValueError(f"Price for {key} cannot be zero.")
        sum += value

    ration = 100 / sum

    result_dict = {}

    for key, value in p_dict.items():
        result_dict[key] = value * ration

    return result_dict


test_dict = {"item1": 50, "item2": 30, "item3": 20}

if __name__ == "__main__":
    print(price_ratio(test_dict))
