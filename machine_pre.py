def main() -> None:
    epsilon = 1

    while (1 + epsilon) != 1:
        epsilon /= 2

    print(f"Machine epsilon: {epsilon}")

    if (1 + epsilon) == 1:
        print("Epsilon is too small to affect the sum.")
    else:
        print("Epsilon is still significant.")


if __name__ == "__main__":
    main()
