from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List
import os


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication via X-API-Key header.

    Skips authentication for health check and docs endpoints.
    """

    def __init__(self, app, api_keys: List[str] = None):
        super().__init__(app)
        self._api_keys = set(api_keys or self._load_keys_from_env())

    @staticmethod
    def _load_keys_from_env() -> List[str]:
        """Load API keys from environment variable"""
        keys_str = os.getenv("API_KEYS", "")
        return [k.strip() for k in keys_str.split(",") if k.strip()]

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check and docs
        if request.url.path in ["/api/v1/health", "/docs", "/redoc", "/openapi.json", "/"]:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Missing API key"}
            )

        # If keys configured, validate against them
        if self._api_keys and api_key not in self._api_keys:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "message": "Invalid API key"}
            )

        return await call_next(request)
