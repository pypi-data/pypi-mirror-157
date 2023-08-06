class Error(Exception):
    pass


class ClientError(Error):
    pass


class ServerError(Error):
    pass


class AuthenticationError(ClientError):
    pass


class CallbackRequiredError(Error):
    """
    Indicates a callback is required but was not present.
    """

class MessagesError(Error):
    """
    Indicates an error related to the Messages class which calls the Vonage Messages API.
    """
