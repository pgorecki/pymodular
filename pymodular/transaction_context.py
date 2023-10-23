from collections import defaultdict
from functools import partial
from typing import Any

from pymodular.dependency_provider import DependencyProvider


class TransactionContext:
    """A context spanning a single transaction for execution of a function"""

    dependency_provider_factory = DependencyProvider

    def __init__(self, dependency_provider=None, *args, **kwargs):
        self.dependency_provider = (
            dependency_provider or self.dependency_provider_factory(*args, **kwargs)
        )
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exception: None
        self._transaction_middlewares = []

    def begin(self):
        """Should be used to start a transaction"""
        self._on_enter_transaction_context(self)

    def end(self, exception=None):
        """Should be used to commit/end a transaction"""
        self._on_exit_transaction_context(self, exception)

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.end(exc_val)

    def _wrap_with_middlewares(self, handler_func):
        p = handler_func
        for middleware in self._transaction_middlewares:
            p = partial(middleware, self, p)
        return p

    def _get_overrides(self, **kwargs):
        overrides = dict(ctx=self)
        overrides.update(kwargs)

        type_match = defaultdict(list)
        for name, value in overrides.items():
            type_match[type(value)].append(value)
        with_unique_type = dict((k, v[0]) for k, v in type_match.items() if len(v) == 1)

        overrides.update(with_unique_type)

        return overrides

    def call(self, func, *func_args, **func_kwargs):
        dp = self.dependency_provider.copy(ctx=self)
        resolved_kwargs = dp.resolve_func_params(func, func_args, func_kwargs)
        p = partial(func, **resolved_kwargs)
        wrapped_handler = self._wrap_with_middlewares(p)
        result = wrapped_handler()
        return result

    def emit(self, event: str, *args, **kwargs):
        """Emit an event"""
        # TODO: Implement event emitting

    def get_dependency(self, identifier: Any) -> Any:
        """Get a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def __getitem__(self, item) -> Any:
        return self.get_dependency(item)
