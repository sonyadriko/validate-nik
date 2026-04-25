from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ValidationDTO(BaseModel):
    status: str = Field(..., description="valid, mismatch, or error")
    reason: Optional[str] = Field(None, description="Validation reason code")
    detail: Optional[str] = Field(None, description="Additional validation detail")


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
    validasi: Optional[ValidationDTO] = Field(None, description="Validation metadata")

    model_config = ConfigDict(json_schema_extra={
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
    })


class ErrorResponse(BaseModel):
    status: bool = False
    message: str
