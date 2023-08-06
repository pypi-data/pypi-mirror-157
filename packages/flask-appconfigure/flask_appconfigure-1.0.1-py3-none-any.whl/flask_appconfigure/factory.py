import flask
from .exceptions import AppConfigurationException
from .base_configurator import BaseConfigurator


class ConfiguratorInformation:
    __slots__ = ("configurator_class", "args", "kwargs")

    def __init__(self, configurator_class, args=(), kwargs={}):
        self.configurator_class = configurator_class
        self.args = args
        self.kwargs = kwargs
        

class ConfiguratorPool:
    def __init__(self):
        self.configuration_information = list()

    def add_configurator(self, configurator_class, args=(), kwargs={}):
        self._check_configurator_class(configurator_class)
        self.configuration_information.append(ConfiguratorInformation(configurator_class, args=args, kwargs=kwargs))
        
    def _check_configurator_class(self, configurator_class):
        if not issubclass(configurator_class, BaseConfigurator):
            raise TypeError(
                f"configurator_class has to be of type {str(BaseConfigurator.__name__)}, not {str(configurator_class.__name__)}"
            )

    def get_configuration_information(self):
        return self.configuration_information


class ApplicationFactory:
    def __init__(self, configurator_pool):
        self.configurator_pool = configurator_pool

    def create_app(self, *args, **kwargs):
        import_name = args[0] if len(args) > 0 else __name__
        main_app = flask.Flask(import_name, **kwargs)
        return self.configure_app(main_app)

    def configure_app(self, main_app):
        try:
            self._configure_app(main_app)
            return main_app
        except Exception as e:
            main_app.logger.critical("Exit App Configuration!", exc_info=e)
            raise AppConfigurationException(str(e))

    def _configure_app(self, main_app):
        for info in self.configurator_pool.get_configuration_information():
            info.configurator_class(main_app).configure_wrapper(*info.args, **info.kwargs)
