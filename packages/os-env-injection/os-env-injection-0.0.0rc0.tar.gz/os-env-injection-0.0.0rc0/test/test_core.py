import os

import pytest

from os_env_injection import read_var_from_os_env_if_not_provided


def test_if_var_and_os_env_var_and_required_then_return_var():
    assert _get_var_value() == read_var_from_os_env_if_not_provided(
        os_env_key=_get_os_key(), var=_get_var_value(), required=True
    )


def test_if_var_and_os_env_var_and_not_required_then_return_var():
    assert _get_var_value() == read_var_from_os_env_if_not_provided(os_env_key=_get_os_key(), var=_get_var_value())


def test_if_var_and_not_os_env_and_required_then_return_var(clean_os_env):
    assert _get_var_value() == read_var_from_os_env_if_not_provided(
        os_env_key=_get_os_key(), var=_get_var_value(), required=True
    )


def test_if_var_and_not_os_env_and_not_required_then_return_var(clean_os_env):
    assert _get_var_value() == read_var_from_os_env_if_not_provided(os_env_key=_get_os_key(), var=_get_var_value())


def test_if_not_var_and_os_env_var_and_required_then_return_os_env_var():
    assert _get_os_env_value() == read_var_from_os_env_if_not_provided(os_env_key=_get_os_key(), required=True)


def test_if_not_var_and_os_env_var_and_not_required_then_return_os_env_var():
    assert _get_os_env_value() == read_var_from_os_env_if_not_provided(os_env_key=_get_os_key())


def test_if_not_var_and_not_os_env_and_required_then_raise_exception(clean_os_env):
    with pytest.raises(OSError):
        read_var_from_os_env_if_not_provided(os_env_key=_get_os_key(), required=True)


def test_if_not_var_and_not_os_env_and_not_required_then_return_none(clean_os_env):
    assert read_var_from_os_env_if_not_provided(os_env_key=_get_os_key()) is None


@pytest.fixture()
def clean_os_env():
    del os.environ[_get_os_key()]


@pytest.fixture(autouse=True)
def setup():
    os.environ[_get_os_key()] = _get_os_env_value()


def _get_os_key() -> str:
    return "TEST_OS_KEY"


def _get_var_value() -> str:
    return "value"


def _get_os_env_value() -> str:
    return "os_value"
