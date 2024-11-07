from typing import Self


class APIException(Exception):
    """
    Exception raised when an error occurred while processing an API request
    """

    def __init__(self: Self, message: str = "An Error occurred while processing the API request") -> None:
        self.message = message
        super().__init__(self.message)


class InvalidAPIResponse(Exception):
    """
    Exception raised when an API response is not valid
    """

    def __init__(self: Self, message: str = "The API response is not valid") -> None:
        self.message = message
        super().__init__(self.message)
