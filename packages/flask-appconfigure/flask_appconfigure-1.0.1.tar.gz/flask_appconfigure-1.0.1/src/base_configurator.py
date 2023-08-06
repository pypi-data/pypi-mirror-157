
class BaseConfigurator:
    ExitOnError = True

    def __init__(self, app):
        self.app = app

    def configure_wrapper(self, *args, **kwargs):
        try:
            self.configure(*args, **kwargs)
        except Exception as e:
            self._log_exception(e)
            self._handle_exception(e)

    def _log_exception(self, exc):
        self.app.logger.error(
            f"Application Configuration in {str(self.__class__.__name__)} failed: {str(exc)} -> [Exit: {str(self.ExitOnError)}]"
        )

    def _handle_exception(self, exc):
        if self.ExitOnError:
            raise exc

    def configure(self):
        raise NotImplementedError("Please subclass from 'BaseConfigurator' and implement your own 'configure' method.")



