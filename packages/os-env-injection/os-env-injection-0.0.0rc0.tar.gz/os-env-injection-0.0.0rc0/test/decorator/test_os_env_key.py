import os
from typing import Optional, Tuple

from os_env_injection import OSEnvInjected, inject_os_env


def test_if_os_env_key_is_specified_then_value_is_taken_from_it():
    os.environ["OS_VAR"] = "foo"
    assert f() == "foo"
    del os.environ["OS_VAR"]


@inject_os_env(keymap={"var": "OS_VAR"})
def f(var: OSEnvInjected = None) -> str:
    return var


def test_complex_scenario():
    os.environ["OS_VAR1"] = "foo"
    os.environ["OS_VAR2"] = "jam"
    assert complex_f(
        None,
        1,
        var2=None,
    ) == ("foo", 1, "jam", None, 3)
    del os.environ["OS_VAR1"]
    del os.environ["OS_VAR2"]


@inject_os_env(keymap={"var1": "OS_VAR1", "var2": "OS_VAR2"})
def complex_f(
    var1: OSEnvInjected, x: int, var2: OSEnvInjected = "spam", var3: Optional[OSEnvInjected] = None, y: int = 3
) -> Tuple[str, int, str, str, int]:
    return var1, x, var2, var3, y
