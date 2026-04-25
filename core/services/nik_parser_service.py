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

    def parse(self, nik_str: str, birth_year: int = None) -> Result:
        """
        Parse NIK string into person data

        Args:
            nik_str: 16-digit NIK string
            birth_year: Override birth year for accurate century (optional)

        Returns:
            Result with data and validation metadata
        """
        # Validate NIK
        nik_result = NIK.create(nik_str)
        if isinstance(nik_result, NIKValidationError):
            return Result.fail(str(nik_result))

        nik = nik_result

        # Determine birth year and validation status
        validation = {"status": "valid", "reason": None, "detail": None}

        if birth_year:
            if birth_year % 100 != nik.raw_year:
                year = birth_year
                validation["status"] = "mismatch"
                validation["reason"] = "dob_mismatch"
                validation["detail"] = f"NIK year ({nik.raw_year:02d}) != provided year ({birth_year % 100:02d})"
            else:
                year = birth_year
                validation["reason"] = "dob_verified"  # User provided birth date and it matches
        else:
            year = nik.year
            validation["reason"] = "nik_only"  # No birth date provided, using NIK calculation

        now = datetime.now()

        # Build birth date
        try:
            birth_date = datetime(year, nik.month, nik.day)
        except ValueError:
            validation["status"] = "error"
            validation["reason"] = "invalid_birthdate"
            # Still try to return data with invalid date
            birth_date = datetime.now()

        # Get region data
        province = self._region_repo.find_province(nik.province_code)
        regency = self._region_repo.find_regency(nik.regency_code)
        district = self._region_repo.find_district(nik.district_code)

        # Build result
        return Result.ok(self._build_person_data(nik, birth_date, now, year, province, regency, district, validation))

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
        """Build person data dict from components"""

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
        next_bday = birth_date.replace(year=now.year)
        if next_bday.date() < now.date():
            next_bday = next_bday.replace(year=now.year + 1)
        days_until = (next_bday.date() - now.date()).days
        ultah_months = days_until // 30
        ultah_days = days_until % 30
        ultah_str = f"{ultah_months} Bulan {ultah_days} Hari Lagi" if days_until > 0 else "Hari Ini!"

        # Zodiac
        zodiac = Zodiac.from_date(birth_date)

        result = {
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

        # Always include validation
        result["validasi"] = validation

        return result
