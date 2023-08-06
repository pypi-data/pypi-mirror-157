from .dependency_registry import DependencyRegistry
from ..utils.sort import Sort
from .registry import Registry

class ComponentRegistry(DependencyRegistry):
    _components: list = []

    def add(self, key_class, value_class=None):
        if value_class is None:
            value_class = key_class

        key = self.get_key(key_class)

        list_dependencies = self.get_dependencies(value_class)
        self._components.append(Registry(key, list_dependencies, value_class))

    def get_components(self) -> list:
        return self._components