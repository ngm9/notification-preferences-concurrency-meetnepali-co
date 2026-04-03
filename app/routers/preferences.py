from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from uuid import UUID
from typing import Optional
from app.middleware.auth import decode_token
from app.models.auth import TokenClaims
from app.models.preferences import PreferencesUpdateRequest, PreferencesResponse
from app.services.preferences_service import fetch_user_preferences, apply_preference_updates

router = APIRouter()


def authorize_access(claims: TokenClaims, user_id: UUID, prefs):
    """Raise 403 if cross-tenant or non-admin accessing another user."""
    if claims.tenant_id != prefs.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if claims.role != "admin" and claims.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/users/{user_id}/preferences")
def get_preferences(
    user_id: UUID,
    claims: TokenClaims = Depends(decode_token),
):
    prefs = fetch_user_preferences(user_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    authorize_access(claims, user_id, prefs)
    data = PreferencesResponse(**prefs.model_dump()).model_dump(mode="json")
    return JSONResponse(content=data, headers={"ETag": f'"{prefs.version}"'})


@router.put("/users/{user_id}/preferences")
def update_preferences(
    user_id: UUID,
    body: PreferencesUpdateRequest,
    claims: TokenClaims = Depends(decode_token),
    if_match: Optional[str] = Header(default=None),
):
    if not if_match:
        raise HTTPException(status_code=428, detail="If-Match header required")

    expected_version = int(if_match.strip('"'))

    prefs = fetch_user_preferences(user_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    authorize_access(claims, user_id, prefs)

    updated = apply_preference_updates(user_id, body, expected_version)
    if not updated:
        raise HTTPException(status_code=412, detail="Precondition Failed")

    data = PreferencesResponse(**updated.model_dump()).model_dump(mode="json")
    return JSONResponse(content=data, headers={"ETag": f'"{updated.version}"'})
