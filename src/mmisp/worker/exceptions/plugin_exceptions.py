class PluginExecutionException(Exception):
    """
    Exception that is raised when a plugin execution fails.
    Can be thrown by the plugin itself.
    """

    def __init__(self, plugin_name: str = "", message: str = ""):
        default_message: str = "The requested Plugin could not be executed successfully."
        if message:
            self.message = message
        elif plugin_name:
            self.message = f"The execution of the requested '{plugin_name}'-Plugin failed."
        else:
            self.message = default_message
        super().__init__(self.message)


class InvalidPluginResult(Exception):
    """
    Exception that is raised when a plugin returns an invalid result that can not be utilized.
    """

    def __init__(self, plugin_name: str = "", message: str = ""):
        default_message: str = "The result of the executed plugin is not valid and can not be utilized."
        if message:
            self.message = message
        elif plugin_name:
            self.message = f"The result provided by the plugin '{plugin_name}' is not valid."
        else:
            self.message = default_message
        super().__init__(self.message)


class PluginRegistrationError(Exception):
    """
    Exception that is raised when a plugin could not be registered.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PluginNotFound(Exception):
    """
    Exception that is raised when a requested plugin could not be found.
    """

    def __init__(self, plugin_name: str = None, message: str = ""):
        default_message: str = "The requested Plugin could not be found."
        if message:
            self.message = message
        elif plugin_name:
            self.message = f"The requested '{plugin_name}'-Plugin could not be found."
        else:
            self.message = default_message
        super().__init__(self.message)


class NotAValidPlugin(Exception):
    """
    Exception that is raised when a class does not match the requirements of a valid plugin.
    """

    def __init__(self, plugin_name: str = None, message: str = ""):
        default_message: str = "The requested Plugin is not a valid plugin. It does not meet the requirements."
        if message:
            self.message = message
        elif plugin_name:
            self.message = (f"The requested '{plugin_name}'-Plugin is not a valid plugin. "
                            f"It does not meet the requirements.")
        else:
            self.message = default_message
        super().__init__(self.message)


class PluginImportError(Exception):
    """
    Exceptions that is raised when a python module of a plugin could not be imported.
    """

    def __init__(self, plugin_module: str = None, message=""):
        default_message: str = "The requested Plugin could not be imported."
        if message:
            self.message = message
        elif plugin_module:
            self.message = (f"The plugin module {plugin_module} could not be imported. "
                            f"Please check it is a valid python module.")
        else:
            self.message = default_message
        super().__init__(self.message)
