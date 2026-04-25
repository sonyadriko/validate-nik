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
