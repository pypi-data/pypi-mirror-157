from typing import Union, List, Optional

PrimitiveValue = Union[str, int, float, bool]
ConfigValue = Union[PrimitiveValue, List[PrimitiveValue]]


def cast_primitive(value: str) -> PrimitiveValue:
    value_lower = value.lower()

    # Attempt to cast to boolean
    if value_lower in ('true', 'false'):
        return value_lower == 'true'

    # Attempt to cast to integer
    try:
        return int(value_lower)
    except ValueError:
        pass

    # Attempt to cast to float
    try:
        return float(value_lower)
    except ValueError:
        pass

    # Finally, return string value is casts fail.
    return value


def cast(value: ConfigValue) -> Optional[ConfigValue]:
    if not value:
        return None

    # List syntax - produce list of primitives
    if ',' in value:
        value = value.split(',')
    if isinstance(value, list):
        return [cast_primitive(val) for val in value]
    return cast_primitive(value)
