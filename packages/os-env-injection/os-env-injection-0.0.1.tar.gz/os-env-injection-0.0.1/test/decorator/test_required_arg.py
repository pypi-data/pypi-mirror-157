import os
from typing import Tuple

import pytest

from os_env_injection import inject_os_env, OSEnvInjected


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        (("foo", "spam", 1, 2), dict()),
        (("foo", "spam", 1), {"y": 2}),
        (("foo", "spam"), {"x": 1, "y": 2}),
        (("foo",), {"var2": "spam", "x": 1, "y": 2}),
        (tuple(), {"var1": "foo", "var2": "spam", "x": 1, "y": 2}),
    ],
)
def test_if_2_injected_os_env_pos_1_2_given_values_then_output_comes_from_values(args_and_kwargs: Tuple[tuple, dict]):
    assert f_2_os_env_pos_1_2(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


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
def test_if_2_injected_os_env_pos_1_2_and_values_are_not_passed_then_output_comes_from_os_env(
    setup_os_env, args_and_kwargs: Tuple[tuple, dict]
):
    assert f_2_os_env_pos_1_2(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


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
def test_if_2_injected_os_env_pos_1_2_and_values_are_not_passed_and_no_os_env_then_raise_exception(
    args_and_kwargs: Tuple[tuple, dict]
):
    with pytest.raises(OSError):
        f_2_os_env_pos_1_2(*args_and_kwargs[0], **args_and_kwargs[1])


@inject_os_env
def f_2_os_env_pos_1_2(
    var1: OSEnvInjected, var2: OSEnvInjected, x: object, y: object
) -> Tuple[str, str, object, object]:
    return var1, var2, x, y


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        (("foo", 1, 2, "spam"), dict()),
        (("foo", 1, 2), {"var2": "spam"}),
        (("foo", 1), {"y": 2, "var2": "spam"}),
        (("foo",), {"x": 1, "y": 2, "var2": "spam"}),
        (tuple(), {"var1": "foo", "x": 1, "y": 2, "var2": "spam"}),
    ],
)
def test_if_2_injected_os_env_pos_1_4_given_values_then_output_comes_from_values(args_and_kwargs: Tuple[tuple, dict]):
    assert f_2_os_env_pos_1_4(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((None, 1, 2, None), dict()),
        ((None, 1, 2), {"var2": None}),
        ((None, 1), {"y": 2, "var2": None}),
        ((None,), {"x": 1, "y": 2, "var2": None}),
        (tuple(), {"var1": None, "x": 1, "y": 2, "var2": None}),
    ],
)
def test_if_2_injected_os_env_pos_1_4_and_values_are_not_passed_then_output_comes_from_os_env(
    setup_os_env, args_and_kwargs: Tuple[tuple, dict]
):
    assert f_2_os_env_pos_1_4(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((None, 1, 2, None), dict()),
        ((None, 1, 2), {"var2": None}),
        ((None, 1), {"y": 2, "var2": None}),
        ((None,), {"x": 1, "y": 2, "var2": None}),
        (tuple(), {"var1": None, "x": 1, "y": 2, "var2": None}),
    ],
)
def test_if_2_injected_os_env_pos_1_4_and_values_are_not_passed_and_no_os_env_then_raise_exception(
    args_and_kwargs: Tuple[tuple, dict]
):
    with pytest.raises(OSError):
        f_2_os_env_pos_1_4(*args_and_kwargs[0], **args_and_kwargs[1])


@inject_os_env
def f_2_os_env_pos_1_4(
    var1: OSEnvInjected, x: object, y: object, var2: OSEnvInjected
) -> Tuple[str, str, object, object]:
    return var1, var2, x, y


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, "foo", "spam", 2), dict()),
        ((1, "foo", "spam"), {"y": 2}),
        ((1, "foo"), {"var2": "spam", "y": 2}),
        ((1,), {"var1": "foo", "var2": "spam", "y": 2}),
        (tuple(), {"x": 1, "var1": "foo", "var2": "spam", "y": 2}),
    ],
)
def test_if_2_injected_os_env_pos_2_3_given_values_then_output_comes_from_values(args_and_kwargs: Tuple[tuple, dict]):
    assert f_2_os_env_pos_2_3(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, None, None, 2), dict()),
        ((1, None, None), {"y": 2}),
        ((1, None), {"var2": None, "y": 2}),
        ((1,), {"var1": None, "var2": None, "y": 2}),
        (tuple(), {"x": 1, "var1": None, "var2": None, "y": 2}),
    ],
)
def test_if_2_injected_os_env_pos_2_3_and_values_are_not_passed_then_output_comes_from_os_env(
    setup_os_env, args_and_kwargs: Tuple[tuple, dict]
):
    assert f_2_os_env_pos_2_3(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, None, None, 2), dict()),
        ((1, None, None), {"y": 2}),
        ((1, None), {"var2": None, "y": 2}),
        ((1,), {"var1": None, "var2": None, "y": 2}),
        (tuple(), {"x": 1, "var1": None, "var2": None, "y": 2}),
    ],
)
def test_if_2_injected_os_env_pos_2_3_and_values_are_not_passed_and_no_os_env_then_raise_exception(
    args_and_kwargs: Tuple[tuple, dict]
):
    with pytest.raises(OSError):
        f_2_os_env_pos_2_3(*args_and_kwargs[0], **args_and_kwargs[1])


@inject_os_env
def f_2_os_env_pos_2_3(
    x: object, var1: OSEnvInjected, var2: OSEnvInjected, y: object
) -> Tuple[str, str, object, object]:
    return var1, var2, x, y


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, "foo", 2, "spam"), dict()),
        ((1, "foo", 2), {"var2": "spam"}),
        ((1, "foo"), {"y": 2, "var2": "spam"}),
        ((1,), {"var1": "foo", "y": 2, "var2": "spam"}),
        (tuple(), {"x": 1, "var1": "foo", "y": 2, "var2": "spam"}),
    ],
)
def test_if_2_injected_os_env_pos_2_4_given_values_then_output_comes_from_values(args_and_kwargs: Tuple[tuple, dict]):
    assert f_2_os_env_pos_2_4(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, None, 2, None), dict()),
        ((1, None, 2), {"var2": None}),
        ((1, None), {"y": 2, "var2": None}),
        ((1,), {"var1": None, "y": 2, "var2": None}),
        (tuple(), {"x": 1, "var1": None, "y": 2, "var2": None}),
    ],
)
def test_if_2_injected_os_env_pos_2_4_and_values_are_not_passed_then_output_comes_from_os_env(
    setup_os_env, args_and_kwargs: Tuple[tuple, dict]
):
    assert f_2_os_env_pos_2_4(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, None, 2, None), dict()),
        ((1, None, 2), {"var2": None}),
        ((1, None), {"y": 2, "var2": None}),
        ((1,), {"var1": None, "y": 2, "var2": None}),
        (tuple(), {"x": 1, "var1": None, "y": 2, "var2": None}),
    ],
)
def test_if_2_injected_os_env_pos_2_4_and_values_are_not_passed_and_no_os_env_then_raise_exception(
    args_and_kwargs: Tuple[tuple, dict]
):
    with pytest.raises(OSError):
        f_2_os_env_pos_2_4(*args_and_kwargs[0], **args_and_kwargs[1])


@inject_os_env
def f_2_os_env_pos_2_4(
    x: object, var1: OSEnvInjected, y: object, var2: OSEnvInjected
) -> Tuple[str, str, object, object]:
    return var1, var2, x, y


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, 2, "foo", "spam"), dict()),
        ((1, 2, "foo"), {"var2": "spam"}),
        ((1, 2), {"var1": "foo", "var2": "spam"}),
        ((1,), {"y": 2, "var1": "foo", "var2": "spam"}),
        (tuple(), {"x": 1, "y": 2, "var1": "foo", "var2": "spam"}),
    ],
)
def test_if_2_injected_os_env_pos_3_4_given_values_then_output_comes_from_values(args_and_kwargs: Tuple[tuple, dict]):
    assert f_2_os_env_pos_3_4(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, 2, None, None), dict()),
        ((1, 2, None), {"var2": None}),
        ((1, 2), {"var1": None, "var2": None}),
        ((1,), {"y": 2, "var1": None, "var2": None}),
        (tuple(), {"x": 1, "y": 2, "var1": None, "var2": None}),
    ],
)
def test_if_2_injected_os_env_pos_3_4_and_values_are_not_passed_then_output_comes_from_os_env(
    setup_os_env, args_and_kwargs: Tuple[tuple, dict]
):
    assert f_2_os_env_pos_3_4(*args_and_kwargs[0], **args_and_kwargs[1]) == ("foo", "spam", 1, 2)


@pytest.mark.parametrize(
    "args_and_kwargs",
    [
        ((1, 2, None, None), dict()),
        ((1, 2, None), {"var2": None}),
        ((1, 2), {"var1": None, "var2": None}),
        ((1,), {"y": 2, "var1": None, "var2": None}),
        (tuple(), {"x": 1, "y": 2, "var1": None, "var2": None}),
    ],
)
def test_if_2_injected_os_env_pos_3_4_and_values_are_not_passed_and_no_os_env_then_raise_exception(
    args_and_kwargs: Tuple[tuple, dict]
):
    with pytest.raises(OSError):
        f_2_os_env_pos_3_4(*args_and_kwargs[0], **args_and_kwargs[1])


@inject_os_env
def f_2_os_env_pos_3_4(
    x: object, y: object, var1: OSEnvInjected, var2: OSEnvInjected
) -> Tuple[str, str, object, object]:
    return var1, var2, x, y


@pytest.fixture
def setup_os_env(monkeypatch: pytest.MonkeyPatch) -> None:
    os.environ["var1"] = "foo"
    os.environ["var2"] = "spam"
    yield
    del os.environ["var1"]
    del os.environ["var2"]
