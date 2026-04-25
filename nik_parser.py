#!/usr/bin/env python3
"""
Standalone Indonesian NIK (Nomor Induk Kependudukan) Parser.

Usage:
    python nik_parser.py 3201010101010001
    python nik_parser.py 3201010101010001 --tanggal-lahir 1985-01-01
    python nik_parser.py --help
"""

import sys
import json
import argparse
import sqlite3
import os
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# ENTITIES & VALUE OBJECTS
# ============================================================================

class Gender(Enum):
    LAKI_LAKI = "LAKI-LAKI"
    PEREMPUAN = "PEREMPUAN"


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

    @classmethod
    def from_date(cls, date: datetime) -> "Zodiac":
        _DATES = [
            (120, cls.CAPRICORN), (219, cls.AQUARIUS), (321, cls.PISCES),
            (420, cls.ARIES), (521, cls.TAURUS), (622, cls.GEMINI),
            (723, cls.CANCER), (823, cls.LEO), (923, cls.VIRGO),
            (1023, cls.LIBRA), (1123, cls.SCORPIO), (1222, cls.SAGITTARIUS),
            (1232, cls.CAPRICORN)
        ]
        mmdd = date.month * 100 + date.day
        for limit, zodiac in _DATES:
            if mmdd <= limit:
                return zodiac
        return cls.CAPRICORN


@dataclass(frozen=True)
class PasaranJawa:
    hari: str
    pasaran: str

    _HARI = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    _PASARAN = ["Legi", "Pahing", "Pon", "Wage", "Kliwon"]
    _REF_DATE = datetime(1900, 1, 1)

    @classmethod
    def from_date(cls, date: datetime) -> "PasaranJawa":
        delta = (date - cls._REF_DATE).days
        hari_idx = (delta + 1) % 7
        pasaran_idx = (delta + 1) % 5
        return cls(hari=cls._HARI[hari_idx], pasaran=cls._PASARAN[pasaran_idx])


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
    def create(cls, value: str):
        try:
            return cls(value)
        except NIKValidationError as e:
            return e

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
        current_yy = datetime.now().year % 100
        if self.raw_year <= current_yy:
            return 2000 + self.raw_year
        return 1900 + self.raw_year


# ============================================================================
# REGION REPOSITORY (SQLite)
# ============================================================================

@dataclass
class Province:
    code: str
    name: str


@dataclass
class Regency:
    code: str
    name: str
    province_code: str
    type: str


@dataclass
class District:
    code: str
    name: str
    regency_code: str


class SQLiteRegionRepository:
    """SQLite-based region repository."""

    def __init__(self, db_path: str = None):
        db_path = db_path or os.path.join(os.path.dirname(__file__), "data", "regions.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found: {db_path}\nRun: python3 scripts/init_db.py")
        self.db_path = db_path

    def find_province(self, code: str) -> Optional[Province]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT code, name FROM provinces WHERE code = ?", (code,)).fetchone()
            if row:
                return Province(row["code"], row["name"])
            return None

    def find_regency(self, code: str) -> Optional[Regency]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT code, name, province_code, type FROM regencies WHERE code = ?", (code,)).fetchone()
            if row:
                return Regency(row["code"], row["name"], row["province_code"], row["type"])
            return None

    def find_district(self, code: str) -> Optional[District]:
        """Find district by code. NIK uses 6-digit, DB uses 7-digit, so use prefix match."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Try exact match first
            row = conn.execute("SELECT code, name, regency_code FROM districts WHERE code = ?", (code,)).fetchone()
            if row:
                return District(code, row["name"], row["regency_code"])
            # Try prefix match
            row = conn.execute("SELECT code, name, regency_code FROM districts WHERE code LIKE ?", (f"{code}%",)).fetchone()
            if row:
                return District(code, row["name"], row["regency_code"])
            return None


# ============================================================================
# NIK PARSER
# ============================================================================

class NIKParser:
    """NIK parser with region database support."""

    BULAN_ID = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

    def __init__(self, db_path: str = None):
        self.region_repo = SQLiteRegionRepository(db_path)

    def parse(self, nik_str: str, tanggal_lahir: str = None) -> dict:
        """
        Parse NIK string into person data.

        Args:
            nik_str: 16-digit NIK string
            tanggal_lahir: Birth date YYYY-MM-DD for verification (optional)
        """
        # Validate NIK
        nik_result = NIK.create(nik_str)
        if isinstance(nik_result, NIKValidationError):
            return {"error": True, "message": str(nik_result)}

        nik = nik_result

        # Determine birth year and validation status
        validation = {"status": "valid", "reason": None, "detail": None}
        birth_year = None

        if tanggal_lahir:
            try:
                birth_date = datetime.strptime(tanggal_lahir, "%Y-%m-%d")
                birth_year = birth_date.year
                if birth_year % 100 != nik.raw_year:
                    validation["status"] = "mismatch"
                    validation["reason"] = "dob_mismatch"
                    validation["detail"] = f"NIK year ({nik.raw_year:02d}) != provided year ({birth_year % 100:02d})"
                else:
                    validation["reason"] = "dob_verified"
            except ValueError:
                validation["status"] = "error"
                validation["reason"] = "invalid_birthdate"
        else:
            birth_year = nik.year
            validation["reason"] = "nik_only"

        now = datetime.now()

        # Build birth date
        try:
            birth_date = datetime(birth_year, nik.month, nik.day)
        except ValueError:
            validation["status"] = "error"
            validation["reason"] = "invalid_birthdate"
            birth_date = now

        # Get region data from database
        province = self.region_repo.find_province(nik.province_code)
        regency = self.region_repo.find_regency(nik.regency_code)
        district = self.region_repo.find_district(nik.district_code)

        # Build result
        return self._build_person_data(nik, birth_date, now, birth_year, province, regency, district, validation)

    def _build_person_data(
        self,
        nik: NIK,
        birth_date: datetime,
        now: datetime,
        year: int,
        province: Optional[Province],
        regency: Optional[Regency],
        district: Optional[District],
        validation: dict
    ) -> dict:
        """Build person data dict from components."""

        lahir = f"{nik.day:02d}/{nik.month:02d}/{nik.raw_year:02d}"
        lahir_lengkap = f"{nik.day} {self.BULAN_ID[nik.month]} {year}"

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
        try:
            next_bday = birth_date.replace(year=now.year)
            if next_bday.date() < now.date():
                next_bday = birth_date.replace(year=now.year + 1)
            days_until = (next_bday.date() - now.date()).days
            ultah_months = days_until // 30
            ultah_days = days_until % 30
            ultah_str = f"{ultah_months} Bulan {ultah_days} Hari Lagi" if days_until > 0 else "Hari Ini!"
        except ValueError:
            ultah_str = "N/A"

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
            },
            "validasi": validation
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Parser NIK (Nomor Induk Kependudukan) Indonesia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  %(prog)s 3201010101010001
  %(prog)s 3201010101010001 --tanggal-lahir 1985-01-01
  %(prog)s 3173086804790005 --json
        """
    )
    parser.add_argument("nik", help="16-digit NIK number")
    parser.add_argument("-t", "--tanggal-lahir", help="Birth date YYYY-MM-DD (optional)")
    parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    nik_parser = NIKParser()
    result = nik_parser.parse(args.nik, args.tanggal_lahir)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("error"):
            print(f"Error: {result['message']}", file=sys.stderr)
            sys.exit(1)

        print("=" * 50)
        print("      HASIL PARSING NIK")
        print("=" * 50)
        print(f"NIK           : {result['nik']}")
        print(f"Jenis Kelamin : {result['kelamin']}")
        print(f"Tanggal Lahir : {result['lahir_lengkap']}")
        print(f"Provinsi      : {result['provinsi']['nama']} ({result['provinsi']['kode']})")
        print(f"Kab/Kota      : {result['kotakab']['nama']} ({result['kotakab']['kode']}) - {result['kotakab']['jenis']}")
        print(f"Kecamatan     : {result['kecamatan']['nama']} ({result['kecamatan']['kode']})")
        print(f"Kode Wilayah  : {result['kode_wilayah']}")
        print(f"No Urut       : {result['nomor_urut']}")
        print("-" * 50)
        print("TAMBAHAN:")
        print(f"  Pasaran      : {result['tambahan']['pasaran']}")
        print(f"  Usia         : {result['tambahan']['usia']}")
        print(f"  Kategori     : {result['tambahan']['kategori_usia']}")
        print(f"  Ultah        : {result['tambahan']['ultah']}")
        print(f"  Zodiak       : {result['tambahan']['zodiak']}")
        print("-" * 50)
        print(f"Validasi      : {result['validasi']['status']} ({result['validasi']['reason']})")


if __name__ == "__main__":
    main()
