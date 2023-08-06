import os
from typing import Optional

import pytest

from os_env_injection import inject_os_env, OSEnvInjected


def test_if_no_input_then_return_os_env():
    assert f() == ("https://www.mydomain.com", "user name", "secret password", None)


def test_if_missing_required_os_env_then_raise_exception():
    del os.environ["OS_ENV_USER"]
    with pytest.raises(OSError):
        f()


def test_if_only_one_value_provided_as_arg_then_return_it():
    assert f("use this instead") == ("use this instead", "user name", "secret password", None)


def test_if_only_one_value_provided_as_kwarg_then_return_it():
    assert f(password="use this instead") == ("https://www.mydomain.com", "user name", "use this instead", None)


def test_if_optional_value_passed_then_return_it():
    assert f(subdomain="use this instead") == (
        "https://www.mydomain.com",
        "user name",
        "secret password",
        "use this instead",
    )


def test_if_optional_value_is_in_os_env_then_return_it():
    os.environ["subdomain"] = "subdomain"
    assert f() == ("https://www.mydomain.com", "user name", "secret password", "subdomain")


def test_if_optional_value_is_passed_and_in_os_env_then_return_passed_value():
    os.environ["subdomain"] = "subdomain"
    assert f(subdomain="use this instead") == (
        "https://www.mydomain.com",
        "user name",
        "secret password",
        "use this instead",
    )


@inject_os_env(keymap={"url": "OS_ENV_URL", "user": "OS_ENV_USER", "password": "OS_ENV_PASSWORD"})
def f(
    url: OSEnvInjected,
    user: OSEnvInjected,
    password: OSEnvInjected,
    subdomain: Optional[OSEnvInjected],
):
    return url, user, password, subdomain


@pytest.fixture(autouse=True)
def setup():
    os.environ["OS_ENV_URL"] = "https://www.mydomain.com"
    os.environ["OS_ENV_USER"] = "user name"
    os.environ["OS_ENV_PASSWORD"] = "secret password"
    yield None
    for v in "OS_ENV_URL", "OS_ENV_USER", "OS_ENV_PASSWORD":
        if v in os.environ.keys():
            del os.environ[v]
