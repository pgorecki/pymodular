import pytest

from pymodular.dependency_provider import DependencyProvider, get_function_parameters


class FooService:
    ...


def foo(a: int, b: str, c: FooService):
    ...


def test_create_provider_with_types():
    foo_service = FooService()
    dp = DependencyProvider(foo_service=foo_service)
    assert dp[FooService] is foo_service
    assert dp["foo_service"] is foo_service


def test_create_provider_with_primitive_arg_raises_error():
    with pytest.raises(ValueError):
        DependencyProvider(1)


def test_create_provider_with_primitive_kwarg():
    dp = DependencyProvider(x=1)
    assert dp["x"] == 1


def test_create_provider_with_class_instance_arg():
    service = FooService()
    dp = DependencyProvider(service)
    assert dp[FooService] is service


def test_create_provider_with_class_instance_karg():
    service = FooService()
    dp = DependencyProvider(service=service)
    assert dp[FooService] is service
    assert dp["service"] is service


def test_create_provider_with_class_instance_arg_and_kwarg_gets_overridden():
    service1 = FooService()
    service2 = FooService()
    dp = DependencyProvider(service1, service=service2)
    assert dp[FooService] is service2
    assert dp["service"] is service2


def test_get_function_parameters():
    params = get_function_parameters(foo)
    assert params["a"] == int
    assert params["b"] == str
    assert params["c"] == FooService


def test_resolve_params_when_empty():
    dp = DependencyProvider()
    assert dp.resolve_func_params(foo) == {}


def test_resolve_params_by_name():
    dp = DependencyProvider(a=1, b="2")
    assert dp.resolve_func_params(foo) == {
        "a": 1,
        "b": "2",
    }


def test_resolve_params_with_func_args():
    dp = DependencyProvider()
    assert dp.resolve_func_params(foo, func_args=(10,)) == {
        "a": 10,
    }


def test_resolve_params_with_func_kargs():
    dp = DependencyProvider()
    assert dp.resolve_func_params(foo, func_kwargs=dict(a=10)) == {
        "a": 10,
    }


def test_resolve_arguments_by_type():
    service = FooService()
    dp = DependencyProvider(service)
    assert dp.resolve_func_params(foo) == {
        "c": service,
    }


def test_resolve_arguments_of_function_without_type_hints():
    def bar(a):
        ...

    dp = DependencyProvider(a=1)
    assert dp.resolve_func_params(bar) == dict(a=1)
