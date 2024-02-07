class APIException(Exception):
    """
    Exception raised when an error occurred while processing an API request
    """

    def __int__(self, message="An Error occurred while processing the API request"):
        self.message = message
        super().__init__(self.message)


class APIRequestFailure(Exception):
    """
    TODO WHY IS THIS NOT USED?
    """

    def __int__(self, message=""):
        self.message = message
        super().__init__(self.message)


class InvalidAPIResponse(Exception):
    """
    Exception raised when an API response is not valid
    """

    def __int__(self, message="The API response is not valid"):
        self.message = message
        super().__init__(self.message)
