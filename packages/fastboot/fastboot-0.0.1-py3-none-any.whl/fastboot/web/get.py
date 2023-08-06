def Get(path=""):
    def get(function):

        def controller_get_function(self):
            def teste():
                return function(self)
            return {
                'path': path,
                'id': '1',
                'function': teste
            }

        controller_get_function.decorators = []
        controller_get_function.decorators.append('Get')

        return controller_get_function


    return get