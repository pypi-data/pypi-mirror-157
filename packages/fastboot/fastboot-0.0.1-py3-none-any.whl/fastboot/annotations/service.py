def Service():
    def wrapper(klass_):
        return klass_
    return wrapper