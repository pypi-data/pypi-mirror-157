from typing import Tuple

import pytest

from os_env_injection import inject_os_env


@pytest.mark.parametrize("args_and_kwargs", [((1, 2), dict()), ((1,), {"y": 2}), (tuple(), {"x": 1, "y": 2})])
def test_if_no_injected_os_env_then_result_is_unchanged(args_and_kwargs: Tuple[tuple, dict]):
    assert f_0_os_env(*args_and_kwargs[0], **args_and_kwargs[1]) == (1, 2)


@inject_os_env
def f_0_os_env(x: object, y: object) -> Tuple[object, object]:
    return x, y
