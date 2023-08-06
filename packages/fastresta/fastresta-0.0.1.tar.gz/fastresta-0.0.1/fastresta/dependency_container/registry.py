
class Registry:

    instance = None


    def __init__(self, key: str, dependencies: list, klass):
        self.key = key
        self.dependencies = dependencies
        self.klass = klass