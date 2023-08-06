import os
import re
from typing import Optional
from yamllib.types import cast, ConfigValue, PrimitiveValue

ENVVAR_REGEX = re.compile(r'(\${[^}^{]+})')


def interpolate(field: PrimitiveValue) -> Optional[ConfigValue]:
    if not isinstance(field, str):
        return field
    next_idx = 0
    result = ''
    while True:
        match = ENVVAR_REGEX.search(field, pos=next_idx)
        if not match:
            result = result or field
            break
        envvar = match.group().strip('$').strip('{').strip('}')
        parts = envvar.split(':')
        default = None
        if len(parts) == 2:
            envvar, default = parts[0], parts[1]
        elif len(parts) > 2:
            envvar, default = parts[0], ':'.join(parts[1:])
        value = os.getenv(envvar, default)
        if not value:
            raise EnvironmentError(f"Environment variable {envvar} must be defined "
                                   f"of have a defined default.")
        result += field[next_idx:match.start()]
        result += str(value)
        next_idx = match.end()
    return cast(result)
