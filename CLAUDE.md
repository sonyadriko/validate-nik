# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize region database (required before first run)
python3 scripts/init_db.py

# Run server
uvicorn main:app --reload

# Run tests
python3 -m pytest

# Run specific test file
python3 -m pytest tests/unit/domain/test_nik_entity.py -v

# Run without coverage
python3 -m pytest --no-cov

# Docker
docker-compose up
```

## Architecture

Layered hexagonal architecture. Domain layer has zero external dependencies.

```
api/
  routes/          - FastAPI endpoints
  middleware/      - API key auth
  dto/             - Response models
  dependencies.py  - DI container
core/
  domain/          - Entities, value objects, interfaces (pure Python)
  services/        - NIK parser service
infrastructure/
  data/            - SQLite region repository
scripts/
  init_db.py       - Download and populate region DB
```

## NIK Structure

Indonesian NIK (Nomor Induk Kependudukan) - 16 digits:

```
PPRRDDDDMMYYXXXX
││││││││││││││││
││││││││││││└└└└─ Sequence (XXXX)
││││││││└└└────── Year (YY)
│││││││└└───────── Month (MM)
│││││└─────────── Day (DD) - >40 = female
│││└──────────── District (6 digits: PPPRDD)
│└────────────── Regency (4 digits: PPPP RR)
└─────────────── Province (2 digits: PP)
```

**Gender**: Day 1-31 = male, 41-71 = female (subtract 40)

**Century calculation**: Without `tanggal_lahir`, estimated from current year. With `tanggal_lahir`, uses provided year.

## API Endpoint

`GET /api/v1/parse?nik={16_digit_nik}&tanggal_lahir={YYYY-MM-DD}`

**Parameters:**
- `nik`: 16-digit NIK (required)
- `tanggal_lahir`: Birth date for verification (optional, format YYYY-MM-DD)

**Response includes `validasi` field:**
```json
{
  "validasi": {
    "status": "valid",      // valid, mismatch, error
    "reason": "dob_verified", // nik_only, dob_verified, dob_mismatch, invalid_birthdate
    "detail": "..."          // Optional detail message
  }
}
```

**Validation mapping for database:**
- `valid` + `nik_only` → NIK parsing without verification
- `valid` + `dob_verified` → User provided date matches NIK
- `mismatch` + `dob_mismatch` → User provided date differs from NIK
- `error` + `invalid_birthdate` → Invalid date (e.g., Feb 30)

## Region Data

SQLite database at `data/regions.db` with 7071 districts.

**District code matching**: NIK uses 6-digit codes, DB uses 7-digit. Service does prefix match.

**Re-download region data:**
```bash
python3 scripts/init_db.py
```

## Deployment

**Docker:**
```bash
docker-compose up
```

**Vercel (serverless):**
- Handler: `api/serverless.py` (uses Mangum)
- Runtime: `python-3.11` (see `runtime.txt`)
- Environment: `API_KEYS` (comma-separated)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Comma-separated API keys (header: `X-API-Key`) | (no auth required) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | (no CORS allowed) |
| `DB_PATH` | Path to regions.db | `data/regions.db` |

**Note:** `.env` file is auto-loaded via `python-dotenv`.

## Authentication

API key authentication is **always enforced** for endpoints except:
- `/api/v1/health` - health check
- `/docs`, `/redoc`, `/openapi.json` - Swagger UI
- `/` - root endpoint

**Behavior:**
- If `API_KEYS` is set → validates against configured keys
- If `API_KEYS` is empty → requires `X-API-Key` header present (any value)
- Returns clean JSON error on auth failure: `{"error": "Unauthorized", "message": "..."}`

**Middleware order** (applied in this order):
1. SecurityHeadersMiddleware (CSP, HSTS, X-Frame-Options, etc.)
2. CORSMiddleware
3. APIKeyMiddleware
