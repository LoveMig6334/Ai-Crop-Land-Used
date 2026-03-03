from torch import cuda


def main() -> None:
    epsilon = 1

    while (1 + epsilon) != 1:
        epsilon /= 2

    print(f"Machine epsilon: {epsilon}")

    if (1 + epsilon) == 1:
        print("Epsilon is too small to affect the sum.")
    else:
        print("Epsilon is still significant.")


def cuda_test() -> None:
    if cuda.is_available():
        print("CUDA is available.")
        print(f"CUDA Device Count: {cuda.device_count()}")
        print(f"Current CUDA Device: {cuda.current_device()}")
        print(f"CUDA Device Name: {cuda.get_device_name(cuda.current_device())}")
    else:
        print("CUDA is not available.")


if __name__ == "__main__":
    main()
    cuda_test()
