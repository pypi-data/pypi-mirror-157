import os

from os_env_injection import inject_os_env, OSEnvInjected


def test_if_var_is_let_to_default_none_value_then_value_comes_from_os_env():
    os.environ["var"] = "foo"
    assert f_default_none() == "foo"
    del os.environ["var"]


@inject_os_env
def f_default_none(var: OSEnvInjected = None) -> str:
    return var


def test_if_var_is_let_to_default_spam_value_then_value_comes_from_it():
    assert f_default_spam() == "spam"


@inject_os_env
def f_default_spam(var: OSEnvInjected = "spam") -> str:
    return var
