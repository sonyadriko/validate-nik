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
