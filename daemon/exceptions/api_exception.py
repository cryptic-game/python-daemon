from starlette.responses import JSONResponse


class APIException(Exception):
    """Base class of all api exceptions"""

    status_code: int
    error: str
    description: str

    def __init__(self, **kwargs):
        """
        :param status_code: http status code
        :param error: error message
        :param kwargs: additional error details
        """

        super().__init__()

        self._kwargs: dict = kwargs

    def make_dict(self) -> dict:
        """Create an error message as specified in the protocol"""

        return {**self._kwargs, "error": self.error}

    def make_response(self) -> JSONResponse:
        """Create a JSONResponse object from this exception containing an error message as specified in the protocol"""

        return JSONResponse(self.make_dict(), status_code=self.status_code)
