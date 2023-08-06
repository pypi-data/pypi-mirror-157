from flask import Flask



class BaseController:
    instance = None
    klass = None
    path = None

    def __init__(self, app: Flask, arguments = []):
        self.app = app
        self.arguments = arguments

    def add_get(self):
        methods_names = self.search_methods('Get')
        for name in methods_names:
            method = getattr(self.instance, name)
            info_method = method()
            self.app.add_url_rule(self.path + info_method.get('path'), info_method.get('id'), info_method.get('function'))


    def add_controller(self):
        print(*self.arguments)
        self.instance = self.klass(*self.arguments)
        self.add_get()



        ##self.app.add_url_rule(self)

        return self.instance

    def search_methods(self, type) -> list[str]:
        response = []
        methods = dir(self.klass)
        for method_name in methods:
            method = getattr(self.klass, method_name)
            try:
                decorators = getattr(method, 'decorators')
                if type in decorators:
                    response.append(method_name)
            except:
                pass
        return response

def RestController(path_controller=''):

    def wrapper(klass_):
        class Controller(BaseController):
            path = path_controller
            klass = klass_
        return Controller

    return wrapper

