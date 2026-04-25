from sqlalchemy import create_engine, Column, String, text
from sqlalchemy.orm import declarative_base, sessionmaker
from core.domain.interfaces import RegionRepository, Province, Regency, District
import os

Base = declarative_base()


class ProvinceDB(Base):
    __tablename__ = 'provinces'
    code = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)


class RegencyDB(Base):
    __tablename__ = 'regencies'
    code = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    province_code = Column(String(10), nullable=False)
    type = Column(String(20), nullable=False)


class DistrictDB(Base):
    __tablename__ = 'districts'
    code = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    regency_code = Column(String(10), nullable=False)


class SQLiteRegionRepository(RegionRepository):
    """SQLite-based region repository"""

    def __init__(self, db_path: str = None):
        db_path = db_path or os.getenv("DB_PATH", "data/regions.db")
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)

    def find_province(self, code: str):
        with self.Session() as session:
            row = session.query(ProvinceDB).filter_by(code=code).first()
            if row:
                return Province(row.code, row.name)
            return None

    def find_regency(self, code: str):
        with self.Session() as session:
            row = session.query(RegencyDB).filter_by(code=code).first()
            if row:
                return Regency(row.code, row.name, row.province_code, row.type)
            return None

    def find_district(self, code: str):
        """Find district by code. NIK uses 6-digit, DB uses 7-digit, so use prefix match."""
        with self.Session() as session:
            # Try exact match first
            row = session.query(DistrictDB).filter_by(code=code).first()
            if row:
                return District(code, row.name, row.regency_code)

            # Try prefix match (NIK code is first 6 digits of DB code)
            row = session.query(DistrictDB).filter(DistrictDB.code.like(f"{code}%")).first()
            if row:
                return District(code, row.name, row.regency_code)

            return None
