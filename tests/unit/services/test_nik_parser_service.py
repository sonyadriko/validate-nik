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
    repo.find_district.return_value = District("320101", "CIBINONG", "3201")
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
    repo.find_district.return_value = District("320101", "CIBINONG", "3201")

    service = NIKParserServiceImpl(repo)
    result = service.parse("3201014101010001")  # day = 41

    assert result.is_valid
    assert result.data["kelamin"] == "PEREMPUAN"
    assert result.data["kotakab"]["jenis"] == "Kota"

def test_parse_unknown_region():
    repo = Mock(spec=RegionRepository)
    repo.find_province.return_value = None
    repo.find_regency.return_value = None
    repo.find_district.return_value = None

    service = NIKParserServiceImpl(repo)
    result = service.parse("9901010101010001")  # Unknown province but valid date

    assert result.is_valid  # Should still parse, just unknown region
    assert result.data["provinsi"]["nama"] == "Tidak Diketahui"
