from typing import Self


class ForbiddenByServerSettings(Exception):
    """
    Exception raised when a requested action was denied by another servers settings
    """

    def __init__(
        self: Self,
        server_id: str | None = None,
        message: str = "A requested action was denied by another servers settings",
    ) -> None:
        if server_id is None:
            self.message: str = message
        else:
            self.message = f"The requested action was denied by the server with id: {server_id} because of its settings"
        super().__init__(self.message)


class ServerNotReachable(Exception):
    """
    Exception raised when a server is not reachable
    """

    def __init__(self: Self, server_id: str | None = None, message: str = "A server is not reachable") -> None:
        if server_id is None:
            self.message = message
        else:
            self.message = f"The server with id: {server_id} is not reachable"
        super().__init__(self.message)


class InvalidServerVersion(Exception):
    """
    Exception raised when a server has an invalid version
    """

    def __init__(
        self: Self,
        server_id: str | None = None,
        message: str = "Another server that was requested has an invalid version",
    ) -> None:
        if server_id is None:
            self.message = message
        else:
            self.message = f"The server with id: {server_id} has an invalid version"
        super().__init__(self.message)
