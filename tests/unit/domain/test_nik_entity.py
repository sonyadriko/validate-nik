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
    with pytest.raises(NIKValidationError, match="hanya boleh angka"):
        NIK("320101010101000a")

def test_nik_extract_gender_female():
    nik = NIK("3201014101010001")  # day = 41 (> 40)
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
