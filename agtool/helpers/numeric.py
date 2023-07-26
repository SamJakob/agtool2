import math


def inverse_factorial(value: int) -> int:
    """
    Computes the inverse factorial of the given integer, `value`.

    :param value: The integer to compute the inverse factorial of.
    :return: The inverse factorial of `value`.
    """
    n = 1
    i = 1
    while n < value:
        i += 1
        n *= i
    return i


def required_permutation_objects(n: int, for_minimum_permutations: int) -> int:
    """
    Returns, for a given number of objects, `n` and a minimum number of total
    permutations, `for_minimum_permutations`, the number of objects that must
    permute together to achieve the minimum number of permutations.

    **Note** that if `n` is sufficiently small, this will throw a

    :param n: The number of objects.
    :param for_minimum_permutations: The minimum number of permutations.
    :return: The number of objects that must permute together to achieve the
        minimum number of permutations.
    """
    x = math.floor(math.factorial(n) / for_minimum_permutations)

    if n < 1 or x < 1:
        raise ValueError(f"n is too small to provide the required minimum number of permutations "
                         f"({for_minimum_permutations}): n = {n}")

    return max(n - inverse_factorial(x), 1)
