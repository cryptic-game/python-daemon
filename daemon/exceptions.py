from fastapi.responses import JSONResponse


class EndpointException(Exception):
    def __init__(self, status_code: int, error: str, **kwargs):
        self._status_code: int = status_code
        self._error: str = error
        self._kwargs: dict = kwargs

    def make_response(self) -> JSONResponse:
        return JSONResponse({**self._kwargs, "error": self._error}, status_code=self._status_code)
