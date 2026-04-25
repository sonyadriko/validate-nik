from fastapi import APIRouter, Query, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from datetime import datetime
from core.services.nik_parser_service import NIKParserServiceImpl
from api.dto.responses import PersonDataResponse
from api.dependencies import get_nik_parser_service

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

router = APIRouter(prefix="/api/v1", tags=["NIK"])


@router.get("/parse", response_model=PersonDataResponse, status_code=200, dependencies=[Depends(api_key_scheme)])
async def parse_nik(
    nik: str = Query(
        ...,
        min_length=16,
        max_length=16,
        pattern=r"^\d+$",
        description="16-digit NIK number"
    ),
    tanggal_lahir: str = Query(
        None,
        max_length=10,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Birth date (YYYY-MM-DD) - optional, for accurate century calculation"
    ),
    service: NIKParserServiceImpl = Depends(get_nik_parser_service)
) -> PersonDataResponse:
    """
    Parse Indonesian NIK (Nomor Induk Kependudukan)

    Returns person biodata extracted from NIK:
    - Gender
    - Birth date
    - Birth location (province, regency, district)
    - Age, zodiac, Javanese pasaran

    **tanggal_lahir (optional)**: Provide birth date for accurate century calculation.
    Without it, century is estimated based on current year.
    """
    # Extract birth year if provided
    birth_year = None
    if tanggal_lahir:
        try:
            birth_date = datetime.strptime(tanggal_lahir, "%Y-%m-%d")
            birth_year = birth_date.year
        except ValueError:
            # Invalid date format - still parse NIK but mark as error
            birth_year = None

    result = service.parse(nik, birth_year=birth_year)

    # Only fail if NIK format is invalid (not for mismatch)
    if not result.is_valid:
        raise HTTPException(status_code=400, detail={
            "status": False,
            "message": result.error
        })

    return PersonDataResponse(**result.data)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "validasi-nik"}
