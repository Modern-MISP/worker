"""
TODO ka was das für exceptions sind
"""
class PluginExecutionException(Exception):
    def __int__(self, message=""):
        self.message = message
        super().__init__(self.message)


class InvalidPluginResult(Exception):
    def __int__(self, message=""):
        self.message = message
        super().__init__(self.message)


class PluginRegistrationError(Exception):
    def __int__(self, message=""):
        self.message = message
        super().__init__(self.message)


class PluginNotFound(Exception):
    def __int__(self, plugin_name: str = None, message="A requested Plugin could not be found"):
        if plugin_name is None:
            self.message = message
        else:
            self.message = f"The requested {plugin_name}-Plugin could not be found"
        super().__init__(self.message)


class NotAValidPlugin(Exception):
    def __int__(self, plugin_name: str = None, message="A requested Plugin was not valid"):
        if plugin_name is None:
            self.message = message
        else:
            self.message = f"The requested {plugin_name}-Plugin is no valid plugin"
        super().__init__(self.message)
