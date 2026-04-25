# NIK Parser API - Design Document

**Date**: 2025-04-25
**Status**: Approved
**Author**: Claude

## Overview

FastAPI-based service to parse Indonesian NIK (Nomor Induk Kependudukan) into structured biodata.
Target: Serverless deployment (Vercel/AWS Lambda) with API key authentication.

## Requirements

| Requirement | Detail |
|-------------|--------|
| Deployment | Serverless (Vercel/Lambda) |
| Data Source | Embedded region data (no network calls) |
| Persistence | Stateless (no database) |
| Auth | API Key via header |
| Testing | Comprehensive coverage |

## Architecture

### Layered Hexagonal Architecture

```
┌─────────────────────────────────────────┐
│           API Layer (FastAPI)            │  Routes, middleware, DTOs
├─────────────────────────────────────────┤
│          Application Layer               │  Use cases, orchestration
├─────────────────────────────────────────┤
│            Domain Layer                  │  Business logic, entities
├─────────────────────────────────────────┤
│      Infrastructure Layer               │  External data, services
└─────────────────────────────────────────┘
```

**Dependency Rule**: Dependencies point inward. Domain knows nothing about outside.

## Domain Layer

### Entities

```python
@dataclass(frozen=True)
class NIK:
    value: str
    # Validation + parsing methods

@dataclass(frozen=True)
class PersonData:
    nik: NIK
    gender: Gender
    birth_date: datetime
    birth_place: Location
    age: Age
    # ... derived data

@dataclass(frozen=True)
class Location:
    province: str
    regency: str
    district: str
    regency_type: RegencyType
```

### Value Objects

```python
class Gender(Enum): LAKI_LAKI, PEREMPUAN
class RegencyType(Enum): KABUPATEN, KOTA
class AgeCategory(Enum): BALITA, ANAK, REMAJA, DEWASA, PARUH_BAYA, LANSIA
```

### Interfaces (DIP)

```python
class RegionRepository(ABC):
    @abstractmethod
    def find_province(self, code: str) -> Optional[Province]

    @abstractmethod
    def find_regency(self, code: str) -> Optional[Regency]

class NIKParserService(ABC):
    @abstractmethod
    def parse(self, nik: str) -> Result[PersonData]
```

## Application Layer

```python
class NIKParserServiceImpl(NIKParserService):
    def __init__(
        self,
        region_repo: RegionRepository,
        calendar: CalendarService = None,
        zodiac_calc: ZodiacCalculator = None
    ):
        self._region_repo = region_repo
        self._calendar = calendar or JavaneseCalendar()
        self._zodiac = zodiac_calc or ZodiacCalculator()
```

## Infrastructure Layer

```python
class EmbeddedRegionRepository(RegionRepository):
    # Region data embedded as Python dicts
    _PROVINCES: Dict[str, Province] = {...}
    _REGENCIES: Dict[str, Regency] = {...}
    _DISTRICTS: Dict[str, District] = {...}
```

## API Layer

### Routes
```python
@router.get("/parse")
async def parse_nik(
    nik: str = Query(..., min_length=16, max_length=16, pattern=r"^\d+$"),
    service: NIKParserService = Depends(get_parser_service)
) -> PersonDataResponse:
```

### Middleware
```python
class APIKeyMiddleware:
    # X-API-Key header validation
```

## Testing

```
tests/
├── unit/
│   ├── domain/test_nik_entity.py
│   ├── domain/test_age_calculator.py
│   ├── services/test_nik_parser.py
│   └── infrastructure/test_region_repo.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_middleware.py
└── fixtures/
    └── nik_samples.py
```

**Coverage**: Domain 100%, Services 95%+, API 80%+

## File Structure

```
validasi-nik/
├── api/
│   ├── dto/
│   ├── middleware/
│   └── routes/
├── core/
│   ├── domain/
│   ├── services/
│   └── utils/
├── infrastructure/
│   └── data/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## SOLID Principles Applied

| Principle | Implementation |
|-----------|----------------|
| SRP | Each class has one reason to change |
| OCP | Open for extension (new parsers), closed for modification |
| LSP | Subtypes interchangeable via interfaces |
| ISP | Small, focused interfaces |
| DIP | Depend on abstractions, inject dependencies |
