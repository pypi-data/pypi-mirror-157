def Component():
    def wrapper(klass_):
        return klass_
    return wrapper