from .dependency_registry import DependencyRegistry
from .registry import Registry

class ControllerRegistry(DependencyRegistry):
    _controllers: list = []

    def add(self, key_class, value_class = None):
        if value_class is None:
            value_class = key_class

        key = self.get_key(key_class)

        list_dependencies = self.get_dependencies(value_class.klass)
        self._controllers.append(Registry(key, list_dependencies, value_class))

    def get_controllers(self) -> list:
        return self._controllers
