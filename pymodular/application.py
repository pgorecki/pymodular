from typing import Any

from pymodular.application_module import ApplicationModule
from pymodular.dependency_provider import DependencyProvider
from pymodular.transaction_context import TransactionContext


class Application(ApplicationModule):
    dependency_provider_class = DependencyProvider

    def __init__(self, name=__name__, dependency_provider=None, **kwargs):
        super().__init__(name)
        self.dependency_provider = (
            dependency_provider or self.dependency_provider_class(**kwargs)
        )
        self._on_enter_transaction_context = lambda ctx: None
        self._on_exit_transaction_context = lambda ctx, exception=None: None
        self._transaction_middlewares = []
        self._modules = set([self])

    def include_module(self, a_module):
        assert isinstance(
            a_module, ApplicationModule
        ), "Can only include ApplicationModule instances"
        self._modules.add(a_module)

    def get_dependency(self, identifier: Any) -> Any:
        """Get a dependency from the dependency provider"""
        return self.dependency_provider.get_dependency(identifier)

    def __getitem__(self, item) -> Any:
        return self.get_dependency(item)

    def on_enter_transaction_context(self, func):
        """
        Decorator for registering a function to be called when entering a transaction context

        :param func:
        :return:
        """
        self._on_enter_transaction_context = func
        return func

    def on_exit_transaction_context(self, func):
        """
        Decorator for registering a function to be called when exiting a transaction context

        :param func:
        :return:
        """
        self._on_exit_transaction_context = func
        return func

    def on(self, event_name):
        def decorator(event_handler):
            """
            Decorator for registering an event handler

            :param event_handler:
            :return:
            """
            # TODO: not yet implemented
            return event_handler

        return decorator

    def transaction_middleware(self, middleware_func):
        """
        Decorator for registering a middleware function to be called when executing a function in a transaction context
        :param middleware_func:
        :return:
        """
        self._transaction_middlewares.insert(0, middleware_func)
        return middleware_func

    def transaction_context(self, **dependencies) -> TransactionContext:
        """
        Creates a transaction context with the application dependencies

        :param dependencies:
        :return:
        """
        dp = self.dependency_provider.copy(**dependencies)
        ctx = TransactionContext(dp)
        ctx._on_enter_transaction_context = self._on_enter_transaction_context
        ctx._on_exit_transaction_context = self._on_exit_transaction_context
        ctx._transaction_middlewares = self._transaction_middlewares
        return ctx
