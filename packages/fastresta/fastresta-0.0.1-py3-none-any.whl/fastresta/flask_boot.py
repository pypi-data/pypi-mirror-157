from .flask_app import create_app
from .dependency_container import DependencyContainer

class FlaskBoot:
    _flask_app = None
    _container = None

    def __init__(self, context):
        self._flask_app = create_app(context)
        self._container = DependencyContainer(self._flask_app)

    def dependency_container(self) -> DependencyContainer:
        return self._container

    def start(self):
        self._flask_app.run()

    def url_map(self):
        return self._flask_app.url_map

    def app(self):
        return self._flask_app