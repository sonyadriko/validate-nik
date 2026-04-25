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
