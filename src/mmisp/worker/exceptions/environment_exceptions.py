class EnvVariableNotFound(Exception):
    """
    Exception raised when an environment variable is not found
    """
    def __init__(self, env_var: str = None, message: str = "A requested environment variable was not found"):
        if env_var is None:
            self.message = message
        else:
            self.message = f"The environment variable \"{env_var}\" could not be found"
        super().__init__(self.message)
