import os
import jwt

from jwt import PyJWKClient
from fastapi import HTTPException, status


AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")

if not AUTH0_DOMAIN:
    raise RuntimeError("AUTH0_DOMAIN is not configured")


ISSUER = f"https://{AUTH0_DOMAIN}/"

JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)


def verify_auth0_token(token: str) -> dict:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={
                "verify_aud": False
            }
        )

        return payload

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 token"
        )