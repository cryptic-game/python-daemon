from fastapi import Request, HTTPException, status, Depends
from fastapi.openapi.models import HTTPBearer
from fastapi.security.base import SecurityBase

from config import API_TOKEN


class HTTPAuthorizationToken(SecurityBase):
    def __init__(self, token: str):
        self.model = HTTPBearer()
        self.scheme_name = self.__class__.__name__
        self.token = token

    async def __call__(self, request: Request) -> bool:
        """
        Check authorization token of a request

        :param request: the request to check
        :return: whether the token is valid
        """

        # accept any request if no token is specified
        if not self.token:
            return True

        # otherwise compare token with authorization header
        authorization: str = request.headers.get("Authorization")
        return authorization and authorization.strip("Bearer ") == self.token


def authorized(is_authorized: HTTPAuthorizationToken = Depends(HTTPAuthorizationToken(API_TOKEN))):
    """
    Endpoint dependency to check the authorization token
    """

    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
