
class DependencyRegistry:

    def get_key(self, key_class):
        return  key_class.__module__ + '.' + key_class.__name__

    def get_dependencies(self, value_class):
        list_class = []

        if(str(type(value_class.__init__)) != "<class 'wrapper_descriptor'>"):
            dependencies: dict = value_class.__init__.__annotations__
            for class_ in list(dependencies.values()):
                list_class.append(self.get_key(class_))
        return list_class

