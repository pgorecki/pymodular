import importlib


class ApplicationModule:
    def __init__(self, name: str):
        self.name = name

    def import_from(self, module_name: str):
        importlib.import_module(module_name)

    def __repr__(self):
        return f"<{self.name} {object.__repr__(self)}>"
