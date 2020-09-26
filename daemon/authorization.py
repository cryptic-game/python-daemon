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
        if not self.token:
            return True

        authorization: str = request.headers.get("Authorization")
        return authorization and authorization.strip("Bearer ") == self.token


def authorized(is_authorized: HTTPAuthorizationToken = Depends(HTTPAuthorizationToken(API_TOKEN))):
    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
