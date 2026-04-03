from fastapi import Header, HTTPException
from jose import JWTError, jwt
from pydantic import ValidationError
from app.config import settings
from app.models.auth import TokenClaims
from typing import Optional

ALLOWED_ROLES = ("user", "admin")


def decode_token(authorization: Optional[str] = Header(default=None)) -> TokenClaims:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    for claim in ("user_id", "tenant_id", "role"):
        if claim not in payload:
            raise HTTPException(status_code=401, detail=f"Missing required claim: {claim}")

    if payload["role"] not in ALLOWED_ROLES:
        raise HTTPException(status_code=401, detail="Invalid role in token")

    try:
        return TokenClaims(
            user_id=payload["user_id"],
            tenant_id=payload["tenant_id"],
            role=payload["role"],
        )
    except (ValueError, ValidationError):
        raise HTTPException(status_code=401, detail="Invalid token claims")
