from ._typing import Modules
from ._common import ALL_MODULES


class ModulesIndex:
    def __init__(self, modules: Modules):
        self._modules = (
            set(modules)
            if not isinstance(modules, str)
            else modules
        )

    def __contains__(self, item: str):
        if self._modules is ALL_MODULES:
            return True
        else:
            return item in self._modules
