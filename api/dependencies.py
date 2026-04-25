from functools import lru_cache
from fastapi import Depends
from core.domain.interfaces import RegionRepository
from core.services.nik_parser_service import NIKParserServiceImpl
from infrastructure.data.sqlite_region_repository import SQLiteRegionRepository


@lru_cache
def get_region_repository() -> RegionRepository:
    """Get singleton region repository instance"""
    return SQLiteRegionRepository()


def get_nik_parser_service(
    repo: RegionRepository = Depends(get_region_repository)
) -> NIKParserServiceImpl:
    """Get NIK parser service with injected repository"""
    return NIKParserServiceImpl(repo)
