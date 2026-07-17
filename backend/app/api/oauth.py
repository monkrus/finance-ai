from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from app.services.oauth import oauth
from app.core.config import settings

router = APIRouter()

@router.get("/login")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get('userinfo')
        if not userinfo:
            userinfo = await oauth.google.userinfo(token=token)
            
        # In a real app, look up user by email in the DB, log them in or register them.
        # Returning user info for demonstration of architectural readiness.
        return {"message": "Google OAuth successful", "email": userinfo["email"], "name": userinfo.get("name")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
