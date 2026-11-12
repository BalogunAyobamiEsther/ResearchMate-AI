
import re
import secrets
from urllib.parse import urlparse

from fastapi import HTTPException, Request, status
from starlette.responses import Response

from backend.app.core.config import settings


SESSION_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")


class AnonymousSessionMiddleware:
    """
    Create or retrieve an anonymous browser session.

    Attach the session cookie to the actual HTTP response,
    including custom responses such as FileResponse.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        session_id = request.cookies.get(
            settings.SESSION_COOKIE_NAME
        )

        is_new_session = (
            not session_id
            or not SESSION_TOKEN_PATTERN.fullmatch(session_id)
        )

        if is_new_session:
            session_id = secrets.token_urlsafe(32)

        scope.setdefault("state", {})["session_id"] = session_id

        async def send_with_session_cookie(message):
            if (
                is_new_session
                and message["type"] == "http.response.start"
            ):
                cookie_response = Response()

                cookie_response.set_cookie(
                    key=settings.SESSION_COOKIE_NAME,
                    value=session_id,
                    max_age=settings.SESSION_COOKIE_MAX_AGE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    secure=settings.SESSION_COOKIE_SECURE,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                    path="/",
                )

                message = dict(message)
                message["headers"] = [
                    *message.get("headers", []),
                    *cookie_response.raw_headers,
                ]

            await send(message)

        await self.app(scope, receive, send_with_session_cookie)


def get_session_id(request: Request) -> str:
    """Retrieve the anonymous session ID created by middleware."""

    session_id = getattr(request.state, "session_id", None)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid browser session is required.",
        )

    return session_id


def require_trusted_origin(request: Request) -> None:
    """
    Protect cookie-authenticated write requests against CSRF.
    """

    origin = request.headers.get("origin")

    if not origin:
        referer = request.headers.get("referer")

        if referer:
            parsed = urlparse(referer)
            origin = f"{parsed.scheme}://{parsed.netloc}"

    if not origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin could not be verified.",
        )

    trusted_origins = {
        allowed_origin.rstrip("/")
        for allowed_origin in settings.ALLOWED_ORIGINS
    }

    if origin.rstrip("/") not in trusted_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not permitted.",
        )
