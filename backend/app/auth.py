from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Header, HTTPException, status
from jwt import PyJWKClient

from app.config import get_settings


@dataclass
class AuthUser:
    user_id: str


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.split(" ", 1)[1].strip()


@lru_cache
def _get_jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def _parse_algorithms(raw_algorithms: str) -> list[str]:
    items = [item.strip() for item in raw_algorithms.split(",") if item.strip()]
    return items or ["RS256"]


def _verify_oidc_token(token: str) -> AuthUser:
    settings = get_settings()
    if not settings.auth_jwks_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AUTH_JWKS_URL is missing")
    if not settings.auth_jwt_issuer:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AUTH_JWT_ISSUER is missing")

    jwks_client = _get_jwks_client(settings.auth_jwks_url)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=_parse_algorithms(settings.auth_jwt_algorithms),
            issuer=settings.auth_jwt_issuer,
            audience=settings.auth_jwt_audience if settings.auth_jwt_audience else None,
            options={"verify_aud": bool(settings.auth_jwt_audience)},
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    return AuthUser(user_id=user_id)


def get_current_user(
    authorization: str | None = Header(default=None),
    x_dev_user_id: str | None = Header(default=None),
) -> AuthUser:
    settings = get_settings()
    provider = settings.auth_provider.lower().strip()

    if provider == "dev":
        return AuthUser(user_id=x_dev_user_id or "dev-user")
    if provider == "oidc":
        token = _extract_bearer_token(authorization)
        return _verify_oidc_token(token)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Unsupported auth provider '{settings.auth_provider}'",
    )
