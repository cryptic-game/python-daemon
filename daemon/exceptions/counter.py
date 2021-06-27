from starlette import status

from exceptions.api_exception import APIException


class CounterNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    error = "counter_not_found"
    description = "The counter for this user could not be found."


class WrongPasswordException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error = "wrong_password"
    description = "The password is not correct."
