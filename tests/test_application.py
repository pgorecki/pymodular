import pytest

from pymodular.application import Application
from pymodular.transaction_context import TransactionContext


class FooService:
    ...


def test_app_transaction_context():
    foo_service = FooService()
    app = Application(foo_service=foo_service)
    ctx = app.transaction_context()

    assert ctx.dependency_provider is not app.dependency_provider
    assert foo_service is ctx[FooService] is app[FooService]


def test_app_transaction_context_with_kwargs():
    foo_service = FooService()
    app = Application(foo_service=foo_service)
    ctx = app.transaction_context(x=1)

    assert ctx.dependency_provider is not app.dependency_provider
    assert (
        foo_service
        is ctx.dependency_provider[FooService]
        is app.dependency_provider[FooService]
    )
    assert ctx.dependency_provider["x"] == 1


def test_app_enter_exit_transaction_context():
    app = Application()

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx):
        ctx.entered = True

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exception=None):
        ctx.exited = True

    with app.transaction_context() as ctx:
        ...

    assert ctx.entered
    assert ctx.exited


def test_app_exception_within_call():
    app = Application()

    @app.on_enter_transaction_context
    def on_enter_transaction_context(ctx):
        ctx.entered = True

    @app.on_exit_transaction_context
    def on_exit_transaction_context(ctx, exception=None):
        if exception:
            ctx.exception = exception

    def foo():
        raise ValueError()

    with pytest.raises(ValueError) as exc:
        with app.transaction_context() as ctx:
            ctx.call(foo)

        assert ctx.entered
        assert ctx.exception is exc


def test_app_uses_middleware():
    app = Application()

    @app.transaction_middleware
    def middleware1(ctx, call_next):
        ctx["buffer"].append(1)
        return call_next()

    @app.transaction_middleware
    def middleware2(ctx, call_next):
        ctx["buffer"].append(2)
        result = call_next()
        ctx["buffer"].append(4)
        return result

    def foo(ctx: TransactionContext):
        ctx["buffer"].append(3)
        return "ok"

    with app.transaction_context(buffer=[]) as ctx:
        result = ctx.call(foo)

    assert ctx["buffer"] == [1, 2, 3, 4]
    assert result == "ok"
