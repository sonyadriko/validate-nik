from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from api.routes.nik import router as nik_router
from api.middleware.auth import APIKeyMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

API_KEYS = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]

# Security scheme for Swagger UI "Authorize" button
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses.
    Skips CSP for docs endpoints to allow Swagger UI.
    """

    _DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Only apply CSP to API endpoints, not docs
        if request.url.path not in self._DOCS_PATHS:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app = FastAPI(
    title="Validasi NIK API",
    description="Indonesian NIK (Nomor Induk Kependudukan) Parser API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_components={
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
    },
    openapi_security=[{"ApiKeyAuth": []}]
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - configure via ALLOWED_ORIGINS env var (comma-separated)
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
_allowed_origins = [origin.strip() for origin in _allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins if _allowed_origins else [],
    allow_credentials=bool(_allowed_origins),
    allow_methods=["GET"],
    allow_headers=["X-API-Key"],
)

# API Key middleware - always added, enforces auth if keys configured
app.add_middleware(APIKeyMiddleware, api_keys=API_KEYS)

# Include routers
app.include_router(nik_router)


@app.get("/")
async def root():
    return {
        "service": "Validasi NIK API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# For serverless deployment
handler = app
