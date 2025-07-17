def price_ratio(p_dict: dict) -> dict:
    sum = 0

    for key, value in p_dict.items():
        if value == 0:
            print(f"Price for {key} cannot be zero.")
            continue
        sum += value

    ratio = 100 / sum
    result_dict = {}

    for key, value in p_dict.items():
        try:
            result_dict[key] = value * ratio
        except Exception as e:
            print(f"Error processing {key}: {e}")
            continue

    return result_dict


test_dict = {"item1": 5, "item2": 3, "item3": 2}
test_dict2 = {"item1": 10, "item2": 0, "item3": 5}
test_dict3 = {"item1": 35, "item2": 14, "item3": 9}
test_dict4 = {"item1": 150, "item2": 780, "item3": 456}


if __name__ == "__main__":
    print(price_ratio(test_dict))
    print(price_ratio(test_dict2))

    print(price_ratio(test_dict3))
    print(price_ratio(test_dict4))
