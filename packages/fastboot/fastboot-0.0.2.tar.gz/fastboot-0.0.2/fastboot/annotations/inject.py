

def Inject():
    def inject_wrapper(function):
        types: dict = function.__annotations__
        def wrapper(*args, **kwargs):
            list_class_components = list(types.values())
            list_components = []
            for class_ in list_class_components:
                component = None
                list_components.append(component)

            arguments_contructor: list = [args[0]] + list_components

            return function(*arguments_contructor)
        return wrapper
    return inject_wrapper