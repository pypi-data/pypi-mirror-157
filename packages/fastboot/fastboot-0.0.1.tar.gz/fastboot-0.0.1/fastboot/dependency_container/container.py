from .controller_registry import ControllerRegistry
from .component_registry import ComponentRegistry
from ..utils.sort import Sort
from .registry import Registry
from ..web.rest_controller import BaseController

class DependencyContainer:

    _dependencies: dict[str, Registry] = {}

    def __init__(self, app):
        self.app = app
        self.controller_registry = ControllerRegistry()
        self.component_registry = ComponentRegistry()


    def register(self, controllers = [], components = []):

        for component in components:
            component(self.component_registry)

        for controller in controllers:
            controller(self.controller_registry)

        self.create()

    def create(self):
        components = Sort.mergeSort(self.component_registry.get_components(), DependencyContainer.callback_sort)

        for component in components:
            self.inject(component)

        controllers = Sort.mergeSort(self.controller_registry.get_controllers(), DependencyContainer.callback_sort)

        for controller in controllers:
            self.inject_controller(controller)

    def inject(self, registry: Registry):
        if len(registry.dependencies) == 0:
            registry.instance = registry.klass()
        else:
            types: dict = registry.klass.__init__.__annotations__

            list_class_components = list(types.values())
            list_components = []
            for class_ in list_class_components:
                component = self.find(class_)
                list_components.append(component)

            registry.instance = registry.klass(*list_components)

        self._dependencies[registry.key] = registry

    def inject_controller(self, registry: Registry):
        if len(registry.dependencies) == 0:
            controller = registry.klass(self.app)
            instance = controller.add_controller()
            registry.instance = instance
        else:
            types: dict = registry.klass.klass.__init__.__annotations__

            list_class_components = list(types.values())
            list_components = []
            for class_ in list_class_components:
                component = self.find(class_)
                list_components.append(component)

            controller: BaseController = registry.klass(self.app, list_components)
            instance = controller.add_controller()
            registry.instance = instance

        self._dependencies[registry.key] = registry

    @staticmethod
    def callback_sort(value_first: Registry, value_second: Registry):
        first_contain_second = value_second.key in value_first.dependencies
        second_contain_first = value_first.key in value_second.dependencies

        if first_contain_second and second_contain_first:
            raise Exception('erro')

        if first_contain_second:
            return Sort.ACCEPT_SECOND

        elif second_contain_first:
            return Sort.ACCEPT_FIRST

        elif len(value_first.dependencies) == 0:
            return Sort.ACCEPT_FIRST
        elif len(value_second.dependencies) == 0:
            return Sort.ACCEPT_SECOND

        return Sort.ACCEPT_ALL

    def find(self, class_):
        key = class_.__module__ + '.' + class_.__name__

        if self._dependencies.get(key) is not None:
            return self._dependencies.get(key).instance


