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

    @classmethod
    def from_date(cls, date: datetime) -> "Zodiac":
        # Cutoff dates: month*100 + day
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
    # Reference: 1900-01-01 = Senin Wage
    _REF_DATE = datetime(1900, 1, 1)

    @classmethod
    def from_date(cls, date: datetime) -> "PasaranJawa":
        delta = (date - cls._REF_DATE).days
        # 1900-01-01 was Monday (Senin), so add 1 to start from correct index
        hari_idx = (delta + 1) % 7
        # Adjust pasaran for 2006-08-21 = Senin Kliwon
        pasaran_idx = (delta + 1) % 5
        return cls(hari=cls._HARI[hari_idx], pasaran=cls._PASARAN[pasaran_idx])
