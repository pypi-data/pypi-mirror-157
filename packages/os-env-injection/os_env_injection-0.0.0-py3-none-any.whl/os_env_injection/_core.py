import os
from typing import Optional


def read_var_from_os_env_if_not_provided(os_env_key: str, var: Optional[str] = None, required: bool = False) -> str:
    if var is None:
        result = os.environ.get(os_env_key, None)
    else:
        result = var

    if result is None and required:
        raise OSError

    return result
