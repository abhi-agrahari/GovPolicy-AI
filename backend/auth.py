import os

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse

from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)

    user_info = token["userinfo"]

    request.session["user_id"] = user_info["sub"]
    request.session["email"] = user_info["email"]

    return RedirectResponse(
        url=os.getenv("FRONTEND_URL")
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logout successful"
    }


@router.get("/me")
async def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    email = request.session.get("email")

    if not user_id:
        return {
            "authenticated": False
        }

    return {
        "authenticated": True,
        "user_id": user_id,
        "email": email
    }