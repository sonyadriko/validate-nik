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
    assert Zodiac.from_date(datetime(2000, 1, 15)).value == "Capricorn"
    assert Zodiac.from_date(datetime(2000, 8, 5)).value == "Leo"
    assert Zodiac.from_date(datetime(2000, 3, 15)).value == "Pisces"

def test_pasaran_sequence():
    from datetime import datetime
    # Known reference: 2006-08-21 = Senin Kliwon
    result = PasaranJawa.from_date(datetime(2006, 8, 21))
    assert result.hari == "Senin"
    assert result.pasaran == "Kliwon"
