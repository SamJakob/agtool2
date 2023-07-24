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
