#!/usr/bin/env python

import datetime as dt

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar, Union


class DateInitError(Exception): pass
class CSVTimeZoneLoaderInitError(Exception): pass

CSVTimeZoneLoaderType: Any
CSVTimeZoneLoaderType = TypeVar('CSVTimeZoneLoaderType', bound='CSVTimeZoneLoaderType')

class CSVTimeZoneLoaderType(ABC):
    
    DIGITS: str

    TZ_FILE_PATH: str
    TZ_TABLE_DATA: List[Dict[str, str]]

    @abstractmethod
    def init(self: CSVTimeZoneLoaderType) -> None: pass

    @abstractmethod
    def timezone(self: CSVTimeZoneLoaderType, td_str: Union[str, None]) -> dt.timezone: pass

    @abstractmethod
    def timedelta(self: CSVTimeZoneLoaderType, td_str: Union[str, None]) -> dt.timedelta: pass

    @abstractmethod
    def get_tz(self: CSVTimeZoneLoaderType, td_str: Union[str, None]) -> str: pass

    @abstractmethod
    def get_td(self: CSVTimeZoneLoaderType, country_code: Union[str, None] = None, timezone: Union[str, None] = None, region: Union[str, None] = None) -> Union[str, None]: pass


DateTimeType: Any
DateTimeType = TypeVar("DateTimeType", bound="DateTimeType")


class DateTimeType(ABC):

    COUNTRY_CODE: str

    DATETIME: dt.datetime

    TZ_NAME: str
    TZ_INFO: str
    
    TIMEDELTA: str
    # TIMESTAMP: int

    CTZ: CSVTimeZoneLoaderType

    def init(self: DateTimeType): pass

    def set_ctz(self: DateTimeType, ctz: CSVTimeZoneLoaderType): pass

    def to_convert(self: DateTimeType, td_str: str): pass

    def dt_from(self: DateTimeType, dt: dt.datetime): pass

    def enhance_tm_sec(self: DateTimeType, sec: int): pass

    def get_year(self: DateTimeType): pass
    
    def get_month(self: DateTimeType): pass
    
    def get_mon(self: DateTimeType, year: int = 0): pass
    
    def get_weekday(self: DateTimeType): pass
    
    def get_day(self: DateTimeType): pass
    
    def get_hours(self: DateTimeType): pass
    
    def get_minutes(self: DateTimeType): pass
    
    def get_seconds(self: DateTimeType): pass
    
    def get_milliseconds(self: DateTimeType): pass