# NIK Parser API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build FastAPI-based NIK parser service with SOLID architecture, comprehensive tests, serverless-ready.

**Architecture:** Layered hexagonal (API → Application → Domain → Infrastructure). All dependencies injected via FastAPI Depends. Domain layer pure Python, no framework coupling.

**Tech Stack:** FastAPI 0.109+, Pydantic 2.5+, Python 3.11+, pytest, pytest-cov, Mangum (serverless adapter)

---

## Prerequisites

### Task 0: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `pytest.ini`

**Step 1: Create requirements.txt**

```txt
fastapi==0.109.2
uvicorn[standard]==0.27.1
pydantic==2.5.3
pydantic-settings==2.1.0
mangum==0.17.0
pytest==7.4.4
pytest-cov==4.1.0
pytest-asyncio==0.23.3
httpx==0.26.0
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "validasi-nik"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.2",
    "uvicorn[standard]>=0.27.1",
    "pydantic>=2.5.3",
    "pydantic-settings>=2.1.0",
    "mangum>=0.17.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.4",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.3",
    "httpx>=0.26.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
asyncio_mode = "auto"
```

**Step 3: Create .gitignore**

```gitignore
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
.env
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
dist/
.vercel/
```

**Step 4: Create pytest.ini**

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts =
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
asyncio_mode = auto
```

**Step 5: Commit**

```bash
git add requirements.txt pyproject.toml .gitignore pytest.ini
git commit -m "chore: add project configuration

- Python 3.11+ requirement
- FastAPI, Pydantic, pytest configured
- Ruff linting setup
- Coverage target: 80%

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Domain Layer

### Task 1: Value Objects

**Files:**
- Create: `core/domain/__init__.py`
- Create: `core/domain/value_objects.py`
- Test: `tests/unit/domain/test_value_objects.py`

**Step 1: Write failing tests**

```python
# tests/unit/domain/test_value_objects.py
import pytest
from core.domain.value_objects import Gender, RegencyType, AgeCategory, Zodiac, PasaranJawa

def test_gender_enum():
    assert Gender.LAKI_LAKI.value == "LAKI-LAKI"
    assert Gender.PEREMPUAN.value == "PEREMPUAN"

def test_regency_type_enum():
    assert RegencyType.KABUPATEN.value == "Kabupaten"
    assert RegencyType.KOTA.value == "Kota"

def test_age_category_from_age():
    assert AgeCategory.from_age(3) == AgeCategory.BALITA
    assert AgeCategory.from_age(10) == AgeCategory.ANAK
    assert AgeCategory.from_age(15) == AgeCategory.REMAJA
    assert AgeCategory.from_age(30) == AgeCategory.DEWASA
    assert AgeCategory.from_age(50) == AgeCategory.PARUH_BAYA
    assert AgeCategory.from_age(70) == AgeCategory.LANSIA

def test_zodiac_from_date():
    from datetime import datetime
    assert Zodiac.from_date(datetime(2000, 1, 15)).name == "Capricorn"
    assert Zodiac.from_date(datetime(2000, 8, 5)).name == "Leo"
    assert Zodiac.from_date(datetime(2000, 3, 15)).name == "Pisces"

def test_pasaran_sequence():
    from datetime import datetime
    # Known reference: 2006-08-21 = Senin Kliwon
    result = PasaranJawa.from_date(datetime(2006, 8, 21))
    assert result.hari == "Senin"
    assert result.pasaran == "Kliwon"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/domain/test_value_objects.py -v
```
Expected: ImportError

**Step 3: Create module init**

```python
# core/domain/__init__.py
from .value_objects import Gender, RegencyType, AgeCategory, Zodiac, PasaranJawa
from .entities import NIK, PersonData, Location

__all__ = [
    "Gender", "RegencyType", "AgeCategory", "Zodiac", "PasaranJawa",
    "NIK", "PersonData", "Location",
]
```

**Step 4: Implement value objects**

```python
# core/domain/value_objects.py
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class Gender(Enum):
    LAKI_LAKI = "LAKI-LAKI"
    PEREMPUAN = "PEREMPUAN"


class RegencyType(Enum):
    KABUPATEN = "Kabupaten"
    KOTA = "Kota"


class AgeCategory(Enum):
    BALITA = "Balita"
    ANAK = "Anak-anak"
    REMAJA = "Remaja"
    DEWASA = "Dewasa"
    PARUH_BAYA = "Paruh Baya"
    LANSIA = "Lansia"

    @classmethod
    def from_age(cls, years: int) -> "AgeCategory":
        if years < 5:
            return cls.BALITA
        elif years < 12:
            return cls.ANAK
        elif years < 18:
            return cls.REMAJA
        elif years < 40:
            return cls.DEWASA
        elif years < 60:
            return cls.PARUH_BAYA
        return cls.LANSIA


class Zodiac(Enum):
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"

    # Cutoff dates: month*100 + day
    _DATES = [
        (120, "Capricorn"), (219, "Aquarius"), (321, "Pisces"),
        (420, "Aries"), (521, "Taurus"), (622, "Gemini"),
        (723, "Cancer"), (823, "Leo"), (923, "Virgo"),
        (1023, "Libra"), (1123, "Scorpio"), (1222, "Sagittarius"),
        (1232, "Capricorn")
    ]

    @classmethod
    def from_date(cls, date: datetime) -> "Zodiac":
        mmdd = date.month * 100 + date.day
        for limit, name in cls._DATES:
            if mmdd <= limit:
                return cls[name]
        return cls.CAPRICORN


@dataclass(frozen=True)
class PasaranJawa:
    hari: str
    pasaran: str

    _HARI = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    _PASARAN = ["Legi", "Pahing", "Pon", "Wage", "Kliwon"]
    # Reference: 1900-01-01 = Senin Wage
    _REF_DATE = datetime(1900, 1, 1)

    @classmethod
    def from_date(cls, date: datetime) -> "PasaranJawa":
        delta = (date - cls._REF_DATE).days
        hari_idx = delta % 7
        pasaran_idx = (delta + 1) % 5  # Adjusted for 2006-08-21 = Senin Kliwon
        return cls(hari=cls._HARI[hari_idx], pasaran=cls._PASARAN[pasaran_idx])
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/domain/test_value_objects.py -v
```
Expected: PASS

**Step 6: Commit**

```bash
git add core/domain/ tests/unit/domain/
git commit -m "feat(domain): add value objects

- Gender, RegencyType, AgeCategory enums
- Zodiac calculator with date cutoffs
- Javanese Pasaran calculator with reference date

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: NIK Entity

**Files:**
- Create: `core/domain/entities.py`
- Test: `tests/unit/domain/test_nik_entity.py`

**Step 1: Write failing tests**

```python
# tests/unit/domain/test_nik_entity.py
import pytest
from datetime import datetime
from core.domain.entities import NIK, NIKValidationError

def test_nik_valid_creation():
    nik = NIK("3201010101010001")
    assert nik.value == "3201010101010001"
    assert nik.province_code == "32"
    assert nik.regency_code == "3201"
    assert nik.district_code == "320101"
    assert nik.raw_day == 1
    assert nik.raw_month == 1
    assert nik.raw_year == 1
    assert nik.sequence == "0001"

def test_nik_invalid_length():
    with pytest.raises(NIKValidationError, match="harus 16 digit"):
        NIK("123")

def test_nik_non_digit():
    with pytest.raises(NIKValidationError, match="hanya angka"):
        NIK("320101010101000a")

def test_nik_extract_gender_female():
    nik = NIK("3201410101010001")  # day > 40
    assert nik.gender == "PEREMPUAN"
    assert nik.day == 1

def test_nik_extract_gender_male():
    nik = NIK("3201010101010001")  # day <= 40
    assert nik.gender == "LAKI-LAKI"
    assert nik.day == 1

def test_nik_year_calculation():
    nik = NIK("3201010101010001")
    # Year based on current date
    assert nik.year in (1901, 2001, 2101)

def test_nik_from_string_method():
    result = NIK.create("3201010101010001")
    assert isinstance(result, NIK)
    assert result.value == "3201010101010001"

def test_nik_create_invalid():
    result = NIK.create("invalid")
    assert isinstance(result, NIKValidationError)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/domain/test_nik_entity.py -v
```
Expected: ImportError

**Step 3: Implement NIK entity**

```python
# core/domain/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union
from .value_objects import Gender


class NIKValidationError(Exception):
    pass


@dataclass(frozen=True)
class NIK:
    value: str

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if len(self.value) != 16:
            raise NIKValidationError("NIK harus 16 digit")
        if not self.value.isdigit():
            raise NIKValidationError("NIK hanya boleh angka")

    @classmethod
    def create(cls, value: str) -> Union["NIK", NIKValidationError]:
        try:
            return cls(value)
        except NIKValidationError as e:
            return NIKValidationError(str(e))

    @property
    def province_code(self) -> str:
        return self.value[:2]

    @property
    def regency_code(self) -> str:
        return self.value[:4]

    @property
    def district_code(self) -> str:
        return self.value[:6]

    @property
    def raw_day(self) -> int:
        return int(self.value[6:8])

    @property
    def raw_month(self) -> int:
        return int(self.value[8:10])

    @property
    def raw_year(self) -> int:
        return int(self.value[10:12])

    @property
    def sequence(self) -> str:
        return self.value[12:16]

    @property
    def gender(self) -> str:
        return Gender.PEREMPUAN.value if self.raw_day > 40 else Gender.LAKI_LAKI.value

    @property
    def day(self) -> int:
        return self.raw_day - 40 if self.raw_day > 40 else self.raw_day

    @property
    def month(self) -> int:
        return self.raw_month

    @property
    def year(self) -> int:
        """Determine century based on current year"""
        current_yy = datetime.now().year % 100
        if self.raw_year <= current_yy:
            return 2000 + self.raw_year
        return 1900 + self.raw_year


@dataclass(frozen=True)
class Location:
    province_code: str
    province_name: str
    regency_code: str
    regency_name: str
    regency_type: str
    district_code: str
    district_name: str


@dataclass(frozen=True)
class Age:
    years: int
    months: int
    days: int
    category: str

    def __str__(self) -> str:
        return f"{self.years} Tahun {self.months} Bulan {self.days} Hari"


@dataclass(frozen=True)
class AdditionalInfo:
    pasaran: str
    usia: str
    kategori_usia: str
    ultah: str
    zodiak: str


@dataclass(frozen=True)
class PersonData:
    nik: str
    kelamin: str
    lahir: str  # DD/MM/YY
    lahir_lengkap: str  # DD Month YYYY
    provinsi: dict
    kotakab: dict
    kecamatan: dict
    kode_wilayah: str
    nomor_urut: str
    tambahan: dict
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/domain/test_nik_entity.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/domain/entities.py tests/unit/domain/test_nik_entity.py
git commit -m "feat(domain): add NIK entity with validation

- 16-digit validation
- Gender extraction (day > 40 = female)
- Province/regency/district code parsing
- Century calculation based on current year

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Domain Interfaces

**Files:**
- Create: `core/domain/interfaces.py`

**Step 1: Create interfaces**

```python
# core/domain/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class Province:
    code: str
    name: str


@dataclass
class Regency:
    code: str
    name: str
    province_code: str
    type: str  # "Kabupaten" or "Kota"


@dataclass
class District:
    code: str
    name: str
    regency_code: str


class RegionRepository(ABC):
    """Interface for region data access"""

    @abstractmethod
    def find_province(self, code: str) -> Optional[Province]:
        pass

    @abstractmethod
    def find_regency(self, code: str) -> Optional[Regency]:
        pass

    @abstractmethod
    def find_district(self, code: str) -> Optional[District]:
        pass


class Result:
    """Simple result type for operations that can fail"""
    def __init__(self, is_valid: bool, data=None, error: str = None):
        self.is_valid = is_valid
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data) -> "Result":
        return cls(True, data=data)

    @classmethod
    def fail(cls, error: str) -> "Result":
        return cls(False, error=error)
```

**Step 2: Commit**

```bash
git add core/domain/interfaces.py
git commit -m "feat(domain): add repository interfaces and result type

- RegionRepository with province/regency/district lookup
- Result type for error handling without exceptions

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Application Layer

### Task 4: NIK Parser Service

**Files:**
- Create: `core/services/__init__.py`
- Create: `core/services/nik_parser_service.py`
- Test: `tests/unit/services/test_nik_parser_service.py`

**Step 1: Write failing tests**

```python
# tests/unit/services/test_nik_parser_service.py
import pytest
from datetime import datetime, date
from unittest.mock import Mock
from core.domain.interfaces import RegionRepository, Province, Regency, District, Result
from core.services.nik_parser_service import NIKParserServiceImpl

@pytest.fixture
def mock_region_repo():
    repo = Mock(spec=RegionRepository)
    repo.find_province.return_value = Province("32", "Jawa Barat")
    repo.find_regency.return_value = Regency("3201", "KABUPATEN BOGOR", "32", "Kabupaten")
    repo.find_district.return_value = District("320101", "CIBINONG")
    return repo

def test_parse_valid_nik(mock_region_repo):
    service = NIKParserServiceImpl(mock_region_repo)
    result = service.parse("3201010101010001")

    assert result.is_valid
    assert result.data["nik"] == "3201010101010001"
    assert result.data["kelamin"] == "LAKI-LAKI"
    assert result.data["provinsi"]["nama"] == "Jawa Barat"
    assert result.data["kotakab"]["nama"] == "KABUPATEN BOGOR"

def test_parse_invalid_nik_length():
    repo = Mock(spec=RegionRepository)
    service = NIKParserServiceImpl(repo)
    result = service.parse("123")

    assert not result.is_valid
    assert "harus 16 digit" in result.error

def test_parse_female_nik():
    repo = Mock(spec=RegionRepository)
    repo.find_province.return_value = Province("32", "Jawa Barat")
    repo.find_regency.return_value = Regency("3201", "KOTA BOGOR", "32", "Kota")
    repo.find_district.return_value = District("320101", "CIBINONG")

    service = NIKParserServiceImpl(repo)
    result = service.parse("3201410101010001")  # day = 41

    assert result.is_valid
    assert result.data["kelamin"] == "PEREMPUAN"
    assert result.data["kotakab"]["jenis"] == "Kota"

def test_parse_unknown_region():
    repo = Mock(spec=RegionRepository)
    repo.find_province.return_value = None
    repo.find_regency.return_value = None
    repo.find_district.return_value = None

    service = NIKParserServiceImpl(repo)
    result = service.parse("9999999999999999")

    assert result.is_valid  # Should still parse, just unknown region
    assert result.data["provinsi"]["nama"] == "Tidak Diketahui"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/services/test_nik_parser_service.py -v
```
Expected: ImportError

**Step 3: Implement NIK parser service**

```python
# core/services/__init__.py
from .nik_parser_service import NIKParserServiceImpl

__all__ = ["NIKParserServiceImpl"]
```

```python
# core/services/nik_parser_service.py
from datetime import datetime
from typing import Optional
from core.domain.interfaces import RegionRepository, Province, Regency, District, Result
from core.domain.value_objects import AgeCategory, Zodiac, PasaranJawa
from core.domain.entities import NIK, NIKValidationError


class NIKParserServiceImpl:
    """Service for parsing NIK into person data"""

    BULAN_ID = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

    def __init__(self, region_repo: RegionRepository):
        self._region_repo = region_repo

    def parse(self, nik_str: str, now: datetime = None) -> Result:
        """
        Parse NIK string into person data

        Args:
            nik_str: 16-digit NIK string
            now: Current datetime (for testing)

        Returns:
            Result with data or error message
        """
        # Validate NIK
        nik_result = NIK.create(nik_str)
        if isinstance(nik_result, NIKValidationError):
            return Result.fail(str(nik_result))

        nik = nik_result
        now = now or datetime.now()

        # Build birth date
        try:
            birth_date = datetime(nik.year, nik.month, nik.day)
        except ValueError:
            return Result.fail("Tanggal lahir tidak valid")

        # Get region data
        province = self._region_repo.find_province(nik.province_code)
        regency = self._region_repo.find_province(nik.regency_code)
        district = self._region_repo.find_district(nik.district_code)

        # Build result
        return Result.ok(self._build_person_data(nik, birth_date, now, province, regency, district))

    def _build_person_data(
        self,
        nik: NIK,
        birth_date: datetime,
        now: datetime,
        province: Optional[Province],
        regency: Optional[Regency],
        district: Optional[District]
    ) -> dict:
        """Build person data dict from components"""

        lahir = f"{nik.day:02d}/{nik.month:02d}/{nik.raw_year:02d}"
        lahir_lengkap = f"{nik.day} {self.BULAN_ID[nik.month]} {nik.year}"

        # Pasaran
        pasaran = PasaranJawa.from_date(birth_date)
        pasaran_str = f"{pasaran.hari} {pasaran.pasaran}, {lahir_lengkap}"

        # Age calculation
        age_delta = now - birth_date
        years = age_delta.days // 365
        remaining_days = age_delta.days % 365
        months = remaining_days // 30
        days = remaining_days % 30
        usia_str = f"{years} Tahun {months} Bulan {days} Hari"

        # Age category
        age_category = AgeCategory.from_age(years)

        # Next birthday
        next_bday = birth_date.replace(year=now.year)
        if next_bday < now.date():
            next_bday = next_bday.replace(year=now.year + 1)
        days_until = (next_bday - now.date()).days
        ultah_months = days_until // 30
        ultah_days = days_until % 30
        ultah_str = f"{ultah_months} Bulan {ultah_days} Hari Lagi" if days_until > 0 else "Hari Ini!"

        # Zodiac
        zodiac = Zodiac.from_date(birth_date)

        return {
            "nik": nik.value,
            "kelamin": nik.gender,
            "lahir": lahir,
            "lahir_lengkap": lahir_lengkap,
            "provinsi": {
                "kode": nik.province_code,
                "nama": province.name if province else "Tidak Diketahui"
            },
            "kotakab": {
                "kode": nik.regency_code,
                "nama": regency.name if regency else "Tidak Diketahui",
                "jenis": regency.type if regency else "??"
            },
            "kecamatan": {
                "kode": nik.district_code,
                "nama": district.name if district else "Tidak Diketahui"
            },
            "kode_wilayah": f"{nik.province_code}.{nik.regency_code[2:4]}.{nik.district_code[4:6]}",
            "nomor_urut": nik.sequence,
            "tambahan": {
                "pasaran": pasaran_str,
                "usia": usia_str,
                "kategori_usia": age_category.value,
                "ultah": ultah_str,
                "zodiak": zodiac.value
            }
        }
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/services/test_nik_parser_service.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add core/services/ tests/unit/services/
git commit -m "feat(service): add NIK parser service

- Parses NIK with region lookup
- Calculates age, zodiac, pasaran
- Returns structured person data
- Handles unknown regions gracefully

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Infrastructure Layer

### Task 5: Embedded Region Repository

**Files:**
- Create: `infrastructure/__init__.py`
- Create: `infrastructure/data/__init__.py`
- Create: `infrastructure/data/embedded_region_repository.py`
- Test: `tests/unit/infrastructure/test_embedded_region_repository.py`

**Step 1: Write failing tests**

```python
# tests/unit/infrastructure/test_embedded_region_repository.py
from infrastructure.data.embedded_region_repository import EmbeddedRegionRepository

def test_find_jawa_barat():
    repo = EmbeddedRegionRepository()
    province = repo.find_province("32")
    assert province is not None
    assert province.code == "32"
    assert province.name == "Jawa Barat"

def test_find_bogor_kabupaten():
    repo = EmbeddedRegionRepository()
    regency = repo.find_regency("3201")
    assert regency is not None
    assert regency.code == "3201"
    assert regency.name == "KABUPATEN BOGOR"
    assert regency.type == "Kabupaten"

def test_find_unknown_province():
    repo = EmbeddedRegionRepository()
    province = repo.find_province("99")
    assert province is None

def test_find_cibinong_district():
    repo = EmbeddedRegionRepository()
    district = repo.find_district("320101")
    assert district is not None
    assert district.name == "CIBINONG"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/infrastructure/test_embedded_region_repository.py -v
```
Expected: ImportError

**Step 3: Download and process region data**

```bash
# Download region data from GitHub
curl -o /tmp/provinces.json https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/provinces.json
curl -o /tmp/regencies.json https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/regencies.json
curl -o /tmp/districts.json https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/districts.json
```

**Step 4: Create repository with embedded data**

```python
# infrastructure/__init__.py
from .data.embedded_region_repository import EmbeddedRegionRepository

__all__ = ["EmbeddedRegionRepository"]
```

```python
# infrastructure/data/__init__.py
from .embedded_region_repository import EmbeddedRegionRepository

__all__ = ["EmbeddedRegionRepository"]
```

```python
# infrastructure/data/embedded_region_repository.py
from core.domain.interfaces import RegionRepository, Province, Regency, District


class EmbeddedRegionRepository(RegionRepository):
    """
    Embedded region data repository.
    Data sourced from: https://github.com/yusufsyaifudin/wilayah-indonesia
    """

    # Embedded province data (sample - full list would be generated)
    _PROVINCES = {
        "11": Province("11", "Aceh"),
        "12": Province("12", "Sumatera Utara"),
        "13": Province("13", "Sumatera Barat"),
        "14": Province("14", "Riau"),
        "15": Province("15", "Jambi"),
        "16": Province("16", "Sumatera Selatan"),
        "17": Province("17", "Bengkulu"),
        "18": Province("18", "Lampung"),
        "19": Province("19", "Kepulauan Bangka Belitung"),
        "21": Province("21", "Kepulauan Riau"),
        "31": Province("31", "DKI Jakarta"),
        "32": Province("32", "Jawa Barat"),
        "33": Province("33", "Jawa Tengah"),
        "34": Province("34", "DI Yogyakarta"),
        "35": Province("35", "Jawa Timur"),
        "36": Province("36", "Banten"),
        "51": Province("51", "Bali"),
        "52": Province("52", "Nusa Tenggara Barat"),
        "53": Province("53", "Nusa Tenggara Timur"),
        "61": Province("61", "Kalimantan Barat"),
        "62": Province("62", "Kalimantan Tengah"),
        "63": Province("63", "Kalimantan Selatan"),
        "64": Province("64", "Kalimantan Timur"),
        "65": Province("65", "Kalimantan Utara"),
        "71": Province("71", "Sulawesi Utara"),
        "72": Province("72", "Sulawesi Tengah"),
        "73": Province("73", "Sulawesi Selatan"),
        "74": Province("74", "Sulawesi Tenggara"),
        "75": Province("75", "Gorontalo"),
        "76": Province("76", "Sulawesi Barat"),
        "81": Province("81", "Maluku"),
        "82": Province("82", "Maluku Utara"),
        "91": Province("91", "Papua"),
        "92": Province("92", "Papua Barat"),
        "93": Province("93", "Papua Selatan"),
        "94": Province("94", "Papua Tengah"),
        "95": Province("95", "Papua Pegunungan"),
        "96": Province("96", "Papua Barat Daya"),
    }

    # Embedded regency data (sample for Jawa Barat - full list generated)
    _REGENCIES = {
        # Jawa Barat (32)
        "3201": Regency("3201", "KABUPATEN BOGOR", "32", "Kabupaten"),
        "3202": Regency("3202", "KABUPATEN SUKABUMI", "32", "Kabupaten"),
        "3203": Regency("3203", "KABUPATEN CIANJUR", "32", "Kabupaten"),
        "3204": Regency("3204", "KABUPATEN BANDUNG", "32", "Kabupaten"),
        "3205": Regency("3205", "KABUPATEN GARUT", "32", "Kabupaten"),
        "3206": Regency("3206", "KABUPATEN TASIKMALAYA", "32", "Kabupaten"),
        "3207": Regency("3207", "KABUPATEN CIAMIS", "32", "Kabupaten"),
        "3208": Regency("3208", "KABUPATEN KUNINGAN", "32", "Kabupaten"),
        "3209": Regency("3209", "KABUPATEN CIREBON", "32", "Kabupaten"),
        "3210": Regency("3210", "KABUPATEN MAJALENGKA", "32", "Kabupaten"),
        "3211": Regency("3211", "KABUPATEN SUMEDANG", "32", "Kabupaten"),
        "3212": Regency("3212", "KABUPATEN INDRAMAYU", "32", "Kabupaten"),
        "3213": Regency("3213", "KABUPATEN SUBANG", "32", "Kabupaten"),
        "3214": Regency("3214", "KABUPATEN PURWAKARTA", "32", "Kabupaten"),
        "3215": Regency("3215", "KABUPATEN KARAWANG", "32", "Kabupaten"),
        "3216": Regency("3216", "KABUPATEN BEKASI", "32", "Kabupaten"),
        "3271": Regency("3271", "KOTA BOGOR", "32", "Kota"),
        "3272": Regency("3272", "KOTA SUKABUMI", "32", "Kota"),
        "3273": Regency("3273", "KOTA BANDUNG", "32", "Kota"),
        "3274": Regency("3274", "KOTA CIREBON", "32", "Kota"),
        "3275": Regency("3275", "KOTA BEKASI", "32", "Kota"),
        "3276": Regency("3276", "KOTA DEPOK", "32", "Kota"),
        "3277": Regency("3277", "KOTA CIMAHI", "32", "Kota"),
        "3278": Regency("3278", "KOTA TASIKMALAYA", "32", "Kota"),
        "3279": Regency("3279", "KOTA BANJAR", "32", "Kota"),
        # DKI Jakarta (31)
        "3171": Regency("3171", "KOTA JAKARTA PUSAT", "31", "Kota"),
        "3172": Regency("3172", "KOTA JAKARTA UTARA", "31", "Kota"),
        "3173": Regency("3173", "KOTA JAKARTA BARAT", "31", "Kota"),
        "3174": Regency("3174", "KOTA JAKARTA SELATAN", "31", "Kota"),
        "3175": Regency("3175", "KOTA JAKARTA TIMUR", "31", "Kota"),
    }

    # Embedded district data (sample)
    _DISTRICTS = {
        # Kabupaten Bogor
        "320101": District("320101", "CIBINONG"),
        "320102": District("320102", "CITEUREUP"),
        "320103": District("320103", "SUKARAJA"),
        "320104": District("320104", "BABAKAN MADANG"),
        "320105": District("320105", "CIJERUK"),
        "320106": District("320106", "LEUWILIANG"),
        "320107": District("320107", "CIAMPEA"),
        "320108": District("320108", "CIBUNG BULANG"),
        "320109": District("320109", "PAMIJAHAN"),
        "320110": District("320110", "RUMPIN"),
        # Kota Bogor
        "327101": District("327101", "BOGOR SELATAN - KOTA"),
        "327102": District("327102", "BOGOR TIMUR - KOTA"),
        "327103": District("327103", "BOGOR UTARA - KOTA"),
        "327104": District("327104", "BOGOR BARAT - KOTA"),
        "327105": District("327105", "BOGOR TENGAH - KOTA"),
        # DKI Jakarta
        "317101": District("317101", "GAMBIR"),
        "317102": District("317102", "SAWAH BESAR"),
        "317103": District("317103", "KEMAYORAN"),
        "317104": District("317104", "SENEN"),
        "317105": District("317105", "CEMPAKA PUTIH"),
        "317106": District("317106", "MENTENG"),
        "317107": District("317107", "JOHAR BARU"),
        "317401": District("317401", "TEBET"),
        "317402": District("317402", "SETIABUDI"),
        "317403": District("317403", "MAMPANG PRAPATAN"),
        "317404": District("317404", "PASAR MINGGU"),
        "317405": District("317405", "KEBAYORAN LAMA"),
        "317406": District("317406", KEBAYORAN BARU"),
        "317407": District("317407", "PESANGGRAHAN"),
        "317408": District("317408", "CILANDAK"),
        "317409": District("317409", "JAGAKARSA"),
        "317410": District("317410", "LUBANG BUAYA"),
    }

    def find_province(self, code: str):
        return self._PROVINCES.get(code)

    def find_regency(self, code: str):
        return self._REGENCIES.get(code)

    def find_district(self, code: str):
        return self._DISTRICTS.get(code)
```

**Note**: The full implementation would include all provinces/regencies/districts. Use the downloaded JSON files to generate complete embedded data.

**Step 5: Run tests to verify they pass**

```bash
pytest tests/unit/infrastructure/test_embedded_region_repository.py -v
```
Expected: PASS

**Step 6: Commit**

```bash
git add infrastructure/ tests/unit/infrastructure/
git commit -m "feat(infrastructure): add embedded region repository

- Embedded province/regency/district data
- No network calls for region lookup
- Fast cold starts for serverless

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## API Layer

### Task 6: DTOs

**Files:**
- Create: `api/__init__.py`
- Create: `api/dto/__init__.py`
- Create: `api/dto/responses.py`
- Test: `tests/unit/api/test_dto.py`

**Step 1: Write failing tests**

```python
# tests/unit/api/test_dto.py
from api.dto.responses import PersonDataResponse, ProvinceDTO, RegencyDTO, DistrictDTO, AdditionalInfoDTO

def test_person_data_response_from_dict():
    data = {
        "nik": "3201010101010001",
        "kelamin": "LAKI-LAKI",
        "lahir": "01/01/01",
        "lahir_lengkap": "1 Januari 2001",
        "provinsi": {"kode": "32", "nama": "Jawa Barat"},
        "kotakab": {"kode": "3201", "nama": "KABUPATEN BOGOR", "jenis": "Kabupaten"},
        "kecamatan": {"kode": "320101", "nama": "CIBINONG"},
        "kode_wilayah": "32.01.01",
        "nomor_urut": "0001",
        "tambahan": {
            "pasaran": "Senin Kliwon, 1 Januari 2001",
            "usia": "23 Tahun 0 Bulan 0 Hari",
            "kategori_usia": "Dewasa",
            "ultah": "6 Bulan 15 Hari Lagi",
            "zodiak": "Capricorn"
        }
    }

    response = PersonDataResponse(**data)
    assert response.nik == "3201010101010001"
    assert response.kelamin == "LAKI-LAKI"
    assert response.provinsi.nama == "Jawa Barat"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/api/test_dto.py -v
```
Expected: ImportError

**Step 3: Implement DTOs**

```python
# api/__init__.py
from .dto.responses import PersonDataResponse
from .routes.nik import router as nik_router

__all__ = ["PersonDataResponse", "nik_router"]
```

```python
# api/dto/__init__.py
from .responses import (
    PersonDataResponse,
    ProvinceDTO,
    RegencyDTO,
    DistrictDTO,
    AdditionalInfoDTO
)

__all__ = [
    "PersonDataResponse",
    "ProvinceDTO",
    "RegencyDTO",
    "DistrictDTO",
    "AdditionalInfoDTO"
]
```

```python
# api/dto/responses.py
from pydantic import BaseModel, Field


class ProvinceDTO(BaseModel):
    kode: str = Field(..., description="Province code")
    nama: str = Field(..., description="Province name")


class RegencyDTO(BaseModel):
    kode: str = Field(..., description="Regency code")
    nama: str = Field(..., description="Regency name")
    jenis: str = Field(..., description="Kabupaten or Kota")


class DistrictDTO(BaseModel):
    kode: str = Field(..., description="District code")
    nama: str = Field(..., description="District name")


class AdditionalInfoDTO(BaseModel):
    pasaran: str = Field(..., description="Javanese pasaran")
    usia: str = Field(..., description="Age string")
    kategori_usia: str = Field(..., description="Age category")
    ultah: str = Field(..., description="Days until next birthday")
    zodiak: str = Field(..., description="Zodiac sign")


class PersonDataResponse(BaseModel):
    nik: str = Field(..., description="NIK number")
    kelamin: str = Field(..., description="Gender")
    lahir: str = Field(..., description="Birth date DD/MM/YY")
    lahir_lengkap: str = Field(..., description="Full birth date")
    provinsi: ProvinceDTO
    kotakab: RegencyDTO
    kecamatan: DistrictDTO
    kode_wilayah: str = Field(..., description="Region code")
    nomor_urut: str = Field(..., description="Sequence number")
    tambahan: AdditionalInfoDTO

    class Config:
        json_schema_extra = {
            "example": {
                "nik": "3201010101010001",
                "kelamin": "LAKI-LAKI",
                "lahir": "01/01/01",
                "lahir_lengkap": "1 Januari 2001",
                "provinsi": {"kode": "32", "nama": "Jawa Barat"},
                "kotakab": {"kode": "3201", "nama": "KABUPATEN BOGOR", "jenis": "Kabupaten"},
                "kecamatan": {"kode": "320101", "nama": "CIBINONG"},
                "kode_wilayah": "32.01.01",
                "nomor_urut": "0001",
                "tambahan": {
                    "pasaran": "Senin Kliwon, 1 Januari 2001",
                    "usia": "23 Tahun 0 Bulan 0 Hari",
                    "kategori_usia": "Dewasa",
                    "ultah": "6 Bulan 15 Hari Lagi",
                    "zodiak": "Capricorn"
                }
            }
        }


class ErrorResponse(BaseModel):
    status: bool = False
    message: str
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/api/test_dto.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add api/dto/ tests/unit/api/test_dto.py
git commit -m "feat(api): add response DTOs

- Pydantic models for API responses
- Field descriptions for OpenAPI docs
- Example included for documentation

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 7: Dependencies

**Files:**
- Create: `api/dependencies.py`

**Step 1: Create dependencies file**

```python
# api/dependencies.py
from functools import lru_cache
from fastapi import Depends
from core.domain.interfaces import RegionRepository
from core.services.nik_parser_service import NIKParserServiceImpl
from infrastructure.data.embedded_region_repository import EmbeddedRegionRepository


@lru_cache
def get_region_repository() -> RegionRepository:
    """Get singleton region repository instance"""
    return EmbeddedRegionRepository()


def get_nik_parser_service(
    repo: RegionRepository = Depends(get_region_repository)
) -> NIKParserServiceImpl:
    """Get NIK parser service with injected repository"""
    return NIKParserServiceImpl(repo)
```

**Step 2: Commit**

```bash
git add api/dependencies.py
git commit -m "feat(api): add dependency injection

- Cached region repository
- Service factory with injected dependencies
- Follows Dependency Inversion Principle

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 8: Routes

**Files:**
- Create: `api/routes/__init__.py`
- Create: `api/routes/nik.py`
- Test: `tests/integration/test_api_endpoints.py`

**Step 1: Write failing tests**

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_parse_nik_valid():
    response = client.get("/parse?nik=3201010101010001")
    assert response.status_code == 200
    data = response.json()
    assert data["nik"] == "3201010101010001"
    assert data["kelamin"] == "LAKI-LAKI"
    assert "provinsi" in data

def test_parse_nik_invalid_length():
    response = client.get("/parse?nik=123")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_parse_nik_missing_param():
    response = client.get("/parse")
    assert response.status_code == 422  # Validation error

def test_api_key_missing():
    response = client.get("/parse?nik=3201010101010001", headers={"X-API-Key": ""})
    assert response.status_code == 401
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/integration/test_api_endpoints.py -v
```
Expected: ImportError

**Step 3: Implement routes**

```python
# api/routes/__init__.py
from .nik import router

__all__ = ["router"]
```

```python
# api/routes/nik.py
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Literal
from core.services.nik_parser_service import NIKParserServiceImpl
from api.dto.responses import PersonDataResponse
from api.dependencies import get_nik_parser_service

router = APIRouter(prefix="/api/v1", tags=["NIK"])


@router.get("/parse", response_model=PersonDataResponse, status_code=200)
async def parse_nik(
    nik: str = Query(
        ...,
        min_length=16,
        max_length=16,
        pattern=r"^\d+$",
        description="16-digit NIK number"
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
    """
    result = service.parse(nik)

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
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/integration/test_api_endpoints.py -v
```
Expected: Partial PASS (auth not implemented yet)

**Step 5: Commit**

```bash
git add api/routes/ tests/integration/test_api_endpoints.py
git commit -m "feat(api): add NIK parsing routes

- GET /api/v1/parse endpoint
- Query validation via Pydantic
- Health check endpoint
- Error handling with proper status codes

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 9: Middleware (API Key Auth)

**Files:**
- Create: `api/middleware/__init__.py`
- Create: `api/middleware/auth.py`
- Modify: `main.py`
- Test: `tests/integration/test_middleware.py`

**Step 1: Write failing tests**

```python
# tests/integration/test_middleware.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_key_valid(monkeypatch):
    # Set test API key
    monkeypatch.setenv("API_KEYS", "test-key-123,another-key")

    response = client.get(
        "/api/v1/parse?nik=3201010101010001",
        headers={"X-API-Key": "test-key-123"}
    )
    assert response.status_code == 200

def test_api_key_missing():
    response = client.get("/api/v1/parse?nik=3201010101010001")
    assert response.status_code == 401

def test_api_key_invalid():
    response = client.get(
        "/api/v1/parse?nik=3201010101010001",
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401

def test_health_check_bypass():
    # Health check should not require API key
    response = client.get("/api/v1/health")
    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/integration/test_middleware.py -v
```
Expected: ImportError

**Step 3: Implement middleware**

```python
# api/middleware/__init__.py
from .auth import APIKeyMiddleware

__all__ = ["APIKeyMiddleware"]
```

```python
# api/middleware/auth.py
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List
import os


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication via X-API-Key header.

    Skips authentication for health check endpoint.
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
        if request.url.path in ["/api/v1/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key"
            )

        if api_key not in self._api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        return await call_next(request)
```

**Step 4: Create main.py**

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.nik import router as nik_router
from api.middleware.auth import APIKeyMiddleware
import os

API_KEYS = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]

app = FastAPI(
    title="Validasi NIK API",
    description="Indonesian NIK (Nomor Induk Kependudukan) Parser API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key middleware (only if keys configured)
if API_KEYS:
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
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/integration/test_middleware.py -v
```
Expected: PASS

**Step 6: Commit**

```bash
git add api/middleware/ main.py tests/integration/test_middleware.py
git commit -m "feat(api): add API key middleware

- X-API-Key header validation
- Configurable via environment variable
- Health check bypassed
- CORS enabled

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Serverless Deployment

### Task 10: Serverless Configuration

**Files:**
- Create: `api/serverless.py`
- Create: `vercel.json`
- Create: `runtime.txt`

**Step 1: Create Vercel serverless adapter**

```python
# api/serverless.py
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")
```

**Step 2: Create Vercel config**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/serverless.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/serverless.py"
    }
  ],
  "env": {
    "API_KEYS": "@api_keys"
  }
}
```

**Step 3: Create runtime config**

```txt
# runtime.txt
python-3.11
```

**Step 4: Commit**

```bash
git add api/serverless.py vercel.json runtime.txt
git commit -m "feat(deploy): add Vercel serverless config

- Mangum adapter for ASGI
- Python 3.11 runtime
- API keys via environment variable

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 11: Documentation

**Files:**
- Create: `README.md`

**Step 1: Create README**

```markdown
# Validasi NIK API

FastAPI-based Indonesian NIK (Nomor Induk Kependudukan) parser.

## Features

- Parse 16-digit NIK into biodata
- Extract: gender, birth date, location (province/regency/district)
- Additional: age, zodiac, Javanese pasaran
- Serverless-ready (Vercel/AWS Lambda)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload
```

## API Usage

```bash
# Parse NIK
curl "http://localhost:8000/api/v1/parse?nik=3201010101010001" \
  -H "X-API-Key: your-api-key"
```

## Response

```json
{
  "nik": "3201010101010001",
  "kelamin": "LAKI-LAKI",
  "lahir": "01/01/01",
  "lahir_lengkap": "1 Januari 2001",
  "provinsi": {"kode": "32", "nama": "Jawa Barat"},
  "kotakab": {"kode": "3201", "nama": "KABUPATEN BOGOR", "jenis": "Kabupaten"},
  "kecamatan": {"kode": "320101", "nama": "CIBINONG"},
  "kode_wilayah": "32.01.01",
  "nomor_urut": "0001",
  "tambahan": {
    "pasaran": "Senin Kliwon, 1 Januari 2001",
    "usia": "23 Tahun 0 Bulan 0 Hari",
    "kategori_usia": "Dewasa",
    "ultah": "6 Bulan 15 Hari Lagi",
    "zodiak": "Capricorn"
  }
}
```

## Architecture

- **Domain**: Business entities and value objects
- **Application**: Use cases (NIK parser service)
- **Infrastructure**: Region data repository
- **API**: FastAPI routes, middleware, DTOs

## License

MIT
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README

- Quick start guide
- API usage examples
- Architecture overview

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Final Tasks

### Task 12: Final Integration Test & Coverage

**Step 1: Run full test suite**

```bash
pytest -v --cov=. --cov-report=html
```

Expected: Coverage ≥ 80%

**Step 2: Test local server**

```bash
uvicorn main:app --reload
```

Test endpoints:
- `GET /` - Welcome message
- `GET /api/v1/health` - Health check
- `GET /api/v1/parse?nik=3201010101010001` - Parse NIK (with API key)
- `GET /docs` - OpenAPI documentation

**Step 3: Lint check**

```bash
ruff check .
```

**Step 4: Type check (optional)**

```bash
mypy .
```

**Step 5: Final commit**

```bash
git add .
git commit -m "chore: final integration complete

- All tests passing
- Coverage target met
- Ready for deployment

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Summary

**Total tasks**: 12
**Estimated time**: 2-3 hours
**Files created**: ~25
**Test files**: ~8
**Coverage target**: 80%+

**Key SOLID implementations**:
- **SRP**: Each class single responsibility
- **OCP**: Extensible via interfaces
- **LSP**: Interfaces properly implemented
- **ISP**: Focused interfaces (RegionRepository)
- **DIP**: Depend on abstractions, inject dependencies
