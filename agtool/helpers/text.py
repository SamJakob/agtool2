import re


def to_lower_snake_case(value: str) -> str:
    """
    Converts a string from UpperCamelCase to lower_snake_case.

    :param value: The string to convert.
    :return: The converted string.
    """
    if len(value) <= 1:
        return value.lower()

    return value[0].lower() + re.sub(r'([A-Z])', lambda x: x.group()[1].lower(), value)


def to_upper_camel_case(value: str) -> str:
    """
    Converts a string from lower_snake_case to UpperCamelCase.

    :param value: The string to convert.
    :return: The converted string.
    """
    if len(value) <= 1:
        return value.upper()

    return value[0].upper() + re.sub(r'_([a-z])', lambda x: x.group()[1].upper(), value[1:])


def string_contains_any_of(value: str, *args: str, case_insensitive: bool = True) -> bool:
    """
    Returns true if any of the given arguments are in the given string.

    :param value: The string to check.
    :param args: The arguments to check for.
    :param case_insensitive: Whether or not to ignore case when checking.
    If set to true, the string and arguments will be converted to lowercase
    before checking to ensure that case is ignored.
    :return: True if any of the arguments are in the string, false otherwise.
    """
    value_normalized = value.lower() if case_insensitive else value

    for arg in args:
        arg_normalized = arg.lower() if case_insensitive else arg
        if arg_normalized in value_normalized:
            return True

    return False
