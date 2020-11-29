from fastapi import Request, HTTPException, status
from fastapi.openapi.models import HTTPBearer
from fastapi.security.base import SecurityBase

from config import API_TOKEN


class HTTPAuthorization(SecurityBase):
    """FastAPI dependency class for http authorization"""

    def __init__(self):
        self.model = HTTPBearer()
        self.scheme_name = self.__class__.__name__
        self._token = API_TOKEN

    async def _check_authorization(self, request: Request) -> bool:
        """
        Check authorization token of a request

        :param request: the request to check
        :return: whether the token is valid
        """

        # accept any request if no token is specified
        if not self._token:
            return True

        # otherwise compare token with authorization header
        authorization: str = request.headers.get("Authorization")
        return authorization and authorization.strip("Bearer ") == self._token

    async def __call__(self, request: Request):
        if not await self._check_authorization(request):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
