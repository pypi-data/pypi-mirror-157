from typing import Tuple, Optional

import pytest

from os_env_injection import inject_os_env, OSEnvInjected


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((None, None, 1, 2), dict()),
        ((None, None, 1), {"y": 2}),
        ((None, None), {"x": 1, "y": 2}),
        ((None,), {"var2": None, "x": 1, "y": 2}),
        (tuple(), {"var1": None, "var2": None, "x": 1, "y": 2}),
    ],
)
def test_if_2_optional_injected_os_env_and_values_are_not_passed_and_no_os_env_then_return_none(
    args_and_kwargs: Tuple[tuple, dict]
):
    assert f_2_optional_os_env(*args_and_kwargs[0], **args_and_kwargs[1]) == (None, None, 1, 2)


@inject_os_env
def f_2_optional_os_env(
    var1: Optional[OSEnvInjected], var2: Optional[OSEnvInjected], x: object, y: object
) -> Tuple[str, str, object, object]:
    return var1, var2, x, y


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((None, None, 1, 2), dict()),
        ((None, None, 1), {"y": 2}),
        ((None, None), {"x": 1, "y": 2}),
        ((None,), {"var2": None, "x": 1, "y": 2}),
        (tuple(), {"var1": None, "var2": None, "x": 1, "y": 2}),
    ],
)
def test_if_1_optional_1_required_injected_os_env_and_values_are_not_passed_and_no_os_env_then_raise_exception(
    args_and_kwargs: Tuple[tuple, dict]
):
    with pytest.raises(OSError):
        f_1_os_env_1_optional_os_env(*args_and_kwargs[0], **args_and_kwargs[1])


@inject_os_env
def f_1_os_env_1_optional_os_env(
    var1: OSEnvInjected, var2: Optional[OSEnvInjected], x: object, y: object
) -> Tuple[str, str, object, object]:
    return var1, var2, x, y
