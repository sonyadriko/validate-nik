from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class Province:
    code: str
    name: str


@dataclass
class Regency:
    code: str
    name: str
    province_code: str
    type: str  # "Kabupaten" or "Kota"


@dataclass
class District:
    code: str
    name: str
    regency_code: str


class RegionRepository(ABC):
    """Interface for region data access"""

    @abstractmethod
    def find_province(self, code: str) -> Optional[Province]:
        pass

    @abstractmethod
    def find_regency(self, code: str) -> Optional[Regency]:
        pass

    @abstractmethod
    def find_district(self, code: str) -> Optional[District]:
        pass


class Result:
    """Simple result type for operations that can fail"""
    def __init__(self, is_valid: bool, data=None, error: str = None):
        self.is_valid = is_valid
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data) -> "Result":
        return cls(True, data=data)

    @classmethod
    def fail(cls, error: str) -> "Result":
        return cls(False, error=error)
