from typing import Optional

from fastapi import HTTPException
from fastapi.security.oauth2 import OAuth2, OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int = None
    email: str = None


class User(BaseModel):
    id: int
    email: str = None
    max_open: int = 0
    admin: bool = False


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
            self,
            token_url: str,
            scheme_name: str = None,
            scopes: dict = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False
            scheme = ""
            param = None

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None

        return param
