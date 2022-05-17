#!/usr/bin/env python


import csv
import io
import os
import datetime as dt
import tempfile
import time

from typing import Any, Dict, List, Tuple, TypeVar, Union
from singletons import CSVTimeZoneLoaderInitError, CSVTimeZoneLoaderType, DateTimeType


CSVTimeZoneLoader: Any
CSVTimeZoneLoader = TypeVar('CSVTimeZoneLoader', bound='CSVTimeZoneLoader')

# ZERO: dt.timedelta
# ZERO = dt.timedelta(0)

class CSVTimeZoneLoader(CSVTimeZoneLoaderType):

    DIGITS: str
    DIGITS = "1234567890"

    TZ_FILE_PATH: str
    TZ_FILE_STREAM: Union[io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None]

    TZ_TABLE_DATA: List[Dict[str, str]]

    def __init__(self: CSVTimeZoneLoader, tzfile: Union[str, io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper]) -> None:
        
        if isinstance(tzfile, str):
        
            self.TZ_FILE_STREAM = None
            self.TZ_FILE_PATH = tzfile

        elif type(tzfile) in (io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper):

            self.TZ_FILE_STREAM = tzfile
            self.TZ_FILE_PATH = ""

        self.init()

    def init(self: CSVTimeZoneLoader) -> None:

        text_stream: Union[io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None]
        text_stream = None

        if self.TZ_FILE_STREAM:

            text_stream = self.TZ_FILE_STREAM

        elif self.TZ_FILE_PATH:

            if self.TZ_FILE_PATH.endswith(".csv"):

                if os.path.exists(self.TZ_FILE_PATH):

                    text_stream = open(self.TZ_FILE_PATH, "r")

        if text_stream:

            with text_stream as csvfile:

                ##* tricky, and bypassing
                if isinstance(csvfile, io.BytesIO) or not getattr(csvfile, "mode", "r") in ("r", "r+", "w+"):

                    ##* tricky, and bypassing
                    if not "b" in getattr(csvfile, "mode", "rb"):

                        raise CSVTimeZoneLoaderInitError(f"Invalid file mode.")

                    csvfile = io.TextIOWrapper(csvfile, encoding="utf-8")

                datz: csv.DictReader
                datz = csv.DictReader(
                    f=csvfile,
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    fieldnames=["country_code","tzname","tzinfo","timedelta"],
                    restkey=None,
                    restval=None
                )

                ##* normalize the data
                self.TZ_TABLE_DATA = [ row for row in datz ]
        else:

            raise CSVTimeZoneLoaderInitError(f"No timezone file specified.")

    def timezone(self: CSVTimeZoneLoader, td_str: str) -> dt.timezone:

        if not td_str:

            raise CSVTimeZoneLoaderInitError(f"No timezone specified.")

        tzname: str
        tzname = self.get_tzname(td_str=td_str)
        return dt.timezone(offset=self.timedelta(td_str=td_str), name=tzname)

    def timedelta(self: CSVTimeZoneLoader, td_str: str) -> dt.timedelta:

        if not td_str:

            raise CSVTimeZoneLoaderInitError(f"No timezone specified.")

        pv: bool
        nv: bool

        pv = td_str.startswith("+")
        nv = td_str.startswith("-")
            
        hours: int
        minutes: int

        td_str = td_str.__getitem__(slice(1, None, 1)) if pv or nv else td_str
        
        #* checker is a string of digits
        for i in range(4):

            if td_str.__getitem__(slice(i, i + 1, 1)) not in self.DIGITS:

                raise CSVTimeZoneLoaderInitError(f"Invalid timezone string {td_str}")

        hours = int(td_str.__getitem__(slice(0, 2, 1)))
        minutes = int(td_str.__getitem__(slice(2, 4, 1)))

        td: dt.timedelta
        td = dt.timedelta(hours=hours, minutes=minutes)

        return td if pv or not nv else -td

    def get_tzname(self: CSVTimeZoneLoader, td_str: str) -> str:

        if not td_str:

            raise CSVTimeZoneLoaderInitError(f"No timezone specified.")

        _: str

        d: Any
        d = td_str.split(",")
        
        tz: str

        if len(d) == 2:

            _, tz = d

            return tz

        else:

            raise CSVTimeZoneLoaderInitError(f"Invalid timezone string {td_str}")

    def get_td(self: CSVTimeZoneLoader, country_code: str = "", tzname: str = "", tzinfo: str = "", timedelta: str = "") -> str:

        if hasattr(self, "TZ_TABLE_DATA"):

            fieldnames: List[str, Any, Any]
            fieldnames = []

            checker: List[str, Any, Any]
            checker = []

            if country_code:

                fieldnames.append("country_code")
                checker.append(country_code)

            if tzname:
                
                fieldnames.append("tzname")
                checker.append(tzname)

            if tzinfo:
                
                fieldnames.append("tzinfo")
                checker.append(tzinfo)

            if timedelta:

                fieldnames.append("timedelta")
                checker.append(timedelta)

            fieldnum: int
            fieldnum = len(fieldnames)

            checknum: int
            checknum = len(checker)

            if checknum == 0:

                raise CSVTimeZoneLoaderInitError(f"No country_code, tzname, or tzinfo specified.")

            for row in self.TZ_TABLE_DATA:

                passing: bool
                passing = True

                ##* checker is a list of strings
                for i in range(fieldnum):

                    if i < checknum:

                        key: str
                        value: str

                        key = fieldnames[i]
                        value = checker[i]

                        if row[key].lower() != value.lower():

                            passing = False
                            break

                    else:

                        break

                if passing:

                    if row["timedelta"] == "":

                        raise CSVTimeZoneLoaderInitError(f"No timedelta found!")

                    if row["tzname"] == "":

                        raise CSVTimeZoneLoaderInitError(f"No timezone name found!")

                    return row["timedelta"] + "," + row["tzname"]

                    # if not tzname:

                    #     if row["tzname"] == "":

                    #         raise CSVTimeZoneLoaderInitError(f"No timezone name found!")

                    #     return row["timedelta"] + "," + row["tzname"]

                    # else:

                    #     return row["timedelta"] + "," + tzname

        else:

            raise CSVTimeZoneLoaderInitError(f"CSVTimeZoneLoader has not been initialized.")
        
        return ""

    def get_tzinfo(self: CSVTimeZoneLoader, country_code: str = "", tzname: str = "") -> str:

        if hasattr(self, "TZ_TABLE_DATA"):

            fieldnames: List[str, Any, Any]
            fieldnames = []

            checker: List[str, Any, Any]
            checker = []

            if country_code:

                fieldnames.append("country_code")
                checker.append(country_code)

            if tzname:
                
                fieldnames.append("tzname")
                checker.append(tzname)

            fieldnum: int
            fieldnum = len(fieldnames)

            checknum: int
            checknum = len(checker)

            if checknum == 0:

                raise CSVTimeZoneLoaderInitError(f"No country_code, tzname, or tzinfo specified.")

            for row in self.TZ_TABLE_DATA:

                passing: bool
                passing = True

                ##* checker is a list of strings
                for i in range(fieldnum):

                    if i < checknum:

                        key: str
                        value: str

                        key = fieldnames[i]
                        value = checker[i]

                        if row[key].lower() != value.lower():

                            passing = False
                            break

                    else:

                        break

                if passing:

                    if row["tzinfo"] == "":

                        raise CSVTimeZoneLoaderInitError(f"No timezone info found!")

                    return row["tzinfo"]

        else:

            raise CSVTimeZoneLoaderInitError(f"CSVTimeZoneLoader has not been initialized.")
        
        return ""


DateTime: Any
DateTime = TypeVar("DateTime", bound="DateTime")


class DateTimeInitError(Exception): pass


class DateTime(DateTimeType):

    COUNTRY_CODE: str

    DATETIME: dt.datetime

    TZ_NAME: str
    TZ_INFO: str
    
    TIMEDELTA: str
    # TIMESTAMP: int

    CTZ: CSVTimeZoneLoaderType

    def __init__(self: DateTime) -> None:

        self.init()

    def __repr__(self: DateTime) -> str:

        return f"<DateTime bound dt.datetime(\"{self.DATETIME}\") at {hex(id(self))}>"

    def __str__(self: DateTime) -> str:

        return self.to_str(
            years=self.get_year(),
            months=self.get_month(),
            days=self.get_day(),
            hours=self.get_hours(),
            minutes=self.get_minutes(),
            seconds=self.get_seconds(),
            milliseconds=0,
            microseconds=0,
        )

    def init(self: DateTime) -> None:

        self.COUNTRY_CODE = ""

        self.TZ_INFO = "Etc/Universal"
        self.TZ_NAME = "UTC"

        self.TIMEDELTA = "+0000,UTC"

        self.DATETIME = dt.datetime.now(dt.timezone.utc)

    def set_ctz(self: DateTime, ctz: CSVTimeZoneLoaderType) -> bool:

        if isinstance(ctz, CSVTimeZoneLoader):
        
            self.CTZ = ctz

            return True

        return False

    def ch_tz(self: DateTime, country_code: str = "", tzinfo: str = "", tzname: str = "") -> bool:

        if country_code:

            self.COUNTRY_CODE = country_code

        if tzinfo:

            self.TZ_INFO = tzinfo
            self.TZ_NAME = self.CTZ.get_tzname(td_str=self.CTZ.get_td(tzinfo=tzinfo))

        if tzname:

            self.TZ_INFO = self.CTZ.get_tzinfo(tzname=tzname)
            self.TZ_NAME = tzname

        return True if country_code or tzinfo or tzname else False

    def str_to_dt(self: DateTime, context: str, tz: Union[dt.timezone, None] = None) -> dt.datetime:

        n: int
        n = len(context)

        z: str
        z = ""

        ##* debug
        # print(context, n)

        # todos: handler timedelta in context

        ##* 29 32
        ##* 2022-05-17 18:58:47.342+07:00
        ##* 2022-05-17 18:58:47.342998+07:00
        ##* 30 33
        ##* 2022-05-17 18:58:47.342+07:00Z
        ##* 2022-05-17 18:58:47.342998+07:00Z
        ##* get utcoffset
        ##* 23 29, 26 32
        ##* :3 4: skip double dots

        ##* change mid empty string
        if context[10] == " ": context = context[:10] +  "T" + context[11:] 

        if n == 19:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%S")
            return d.replace(tzinfo=tz) if tz else d
        
        elif n == 20:
        
            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%SZ")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 23 or n == 26:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%S.%f")
            return d.replace(tzinfo=tz) if tz else d

        elif n == 24 or n == 27:

            d: dt.datetime
            d = dt.datetime.strptime(context, "%Y-%m-%dT%H:%M:%S.%fZ")
            return d.replace(tzinfo=tz) if tz else d

        elif (n == 28 or n == 29) and context[26] == "0":

            z = context[23:28]
            context = context[:23] + context[28:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        elif (n == 29 or n == 30) and context[26] == ":":

            z = context[23:29]
            z = z[:3] + z[4:]
            context = context[:23] + context[29:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        elif (n == 31 or n == 32) and context[29] == "0":

            z = context[26:31]            
            context = context[:26] + context[31:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        elif (n == 32 or n == 33) and context[29] == ":":

            z = context[26:32]
            z = z[:3] + z[4:]
            
            context = context[:26] + context[32:]

            tz: dt.timezone
            tz = self.CTZ.timezone(td_str=self.CTZ.get_td(timedelta=z))

            ##* fallback
            return self.str_to_dt(context=context, tz=tz)

        else:

            raise DateTimeInitError(f"Invalid datetime string.")

    def to_dt(self: DateTime, td_str: str = "") -> dt.datetime:

        if td_str:

            return self.DATETIME.replace(tzinfo=self.CTZ.timezone(td_str=td_str)) \
                + self.CTZ.timedelta(td_str=td_str) \
                    - self.CTZ.timedelta(td_str=self.TIMEDELTA)

        return self.DATETIME

    def set_dt_from(self: DateTime, dt: dt.datetime) -> None:

        tzname: str
        tzname = dt.tzname()

        if tzname:

            td: str
            td = self.CTZ.get_td(tzname=tzname)

            # self.DATETIME = dt.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA)) \
            #     + self.CTZ.timedelta(td_str=self.TIMEDELTA) \
            #         - self.CTZ.timedelta(td_str=td)

            self.DATETIME = dt

            self.TZ_INFO = self.CTZ.get_tzinfo(tzname=tzname)
            self.TZ_NAME = tzname

            self.TIMEDELTA = td

        else:

            raise DateTimeInitError(f"No timezone specified.")

    def ch_dt_from(self: DateTime, dt: dt.datetime) -> None:

        tzname: str
        tzname = dt.tzname()

        if tzname:

            td: str
            td = self.CTZ.get_td(tzname=tzname)

            self.DATETIME = dt.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA)) \
                + self.CTZ.timedelta(td_str=self.TIMEDELTA) \
                    - self.CTZ.timedelta(td_str=td)

            # self.TZ_INFO = self.CTZ.get_tzname(td_str=td)
            # self.TZ_NAME = tzname

            # self.TIMEDELTA = td

        else:

            raise DateTimeInitError(f"No timezone specified.")

    def to_str(self: DateTime, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0, microseconds: int = 0) -> str:

        _Y: int
        _m: int
        _d: int
        _H: int
        _M: int
        _S: int
        _s: int
        _f: int

        ##* normalize datetime
        _Y, _m, _d, _H, _M, _S, _s, _f = self.date_fix(
            years=years,
            months=months,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds
        )

        Y: str
        Y = str(_Y).zfill(4)

        m: str
        m = str(_m).zfill(2)
        
        d: str
        d = str(_d).zfill(2)

        H: str
        H = str(_H).zfill(2)
        
        M: str
        M = str(_M).zfill(2)

        S: str
        S = str(_S).zfill(2)

        s: str
        s = str(_s).zfill(3)

        f: str
        f = str(_f).zfill(3)

        context: str

        if s != "000":

            if f != "000":
                
                context = f"{Y}-{m}-{d}T{H}:{M}:{S}.{s}{f}"

            else:

                context = f"{Y}-{m}-{d}T{H}:{M}:{S}.{s}"

        else:

            context = f"{Y}-{m}-{d}T{H}:{M}:{S}"

        context = context + "Z" if self.TZ_NAME == "UTC" else context

        return context

    def date_fix(self: DateTime, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0, microseconds: int = 0) -> Tuple[int]:

        milliseconds += microseconds // 1000
        microseconds = microseconds % 1000

        seconds += milliseconds // 1000
        milliseconds = milliseconds % 1000

        minutes += seconds // 60
        seconds = seconds % 60

        hours += minutes // 60
        minutes = minutes % 60

        days += hours // 24
        hours = hours % 24

        months += days // 30
        days = days % 30

        years += months // 12
        months = months % 12

        #**********************************************************************#
        #* LEAP YEAR                                                          *#
        #**********************************************************************#

        k: int
        k = self.get_mon(years=years, months=months)

        if days > k:

            days = days - k
            months += 1

        if months > 12:

            months = months - 12
            years += 1
        
        #**********************************************************************#
        #* LEAP YEAR                                                          *#
        #**********************************************************************#

        return (years, months, days, hours, minutes, seconds, milliseconds, microseconds)

    def enhance_tm_sec(self: DateTime, sec: int) -> dt.datetime:

        return self.enhance_tm_auto(sec=sec)

    def enhance_tm_ms(self: DateTime, ms: int) -> dt.datetime:

        return self.enhance_tm_auto(ms=ms)

    def enhance_tm_us(self: DateTime, us: int) -> dt.datetime:

        return self.enhance_tm_auto(us=us)

    def enhance_tm_auto(self: DateTime, sec: int = 0, ms: int = 0, us: int = 0) -> dt.datetime:

        Y: int
        m: int
        d: int
        H: int
        M: int
        S: int
        s: int
        f: int

        Y = self.get_year()
        m = self.get_month()
        d = self.get_day()
        H = self.get_hours()
        M = self.get_minutes()
        S = self.get_seconds() + sec
        s = ms
        f = us

        ##* date normalize to stringify
        # context: str
        # context = self.to_str(
        #     years=Y,
        #     months=m,
        #     days=d,
        #     hours=H,
        #     minutes=M,
        #     seconds=S,
        #     milliseconds=s,
        #     microseconds=f
        # )

        ##* date normalize
        Y, m, d, H, M, S, s, f = self.date_fix(
            years=Y,
            months=m,
            days=d,
            hours=H,
            minutes=M,
            seconds=S,
            milliseconds=s,
            microseconds=f
        )
        
        tm: time.struct_time
        tm = self.get_struct_tm(
            years=Y,
            months=m,
            days=d,
            hours=H,
            minutes=M,
            seconds=S,
            weekdays=self.get_weekday(years=Y, months=m, days=d),
            yeardays=self.get_yearday(years=Y, months=m, days=d),

            ##* tricky, idk, but still works necessary
            is_dst=self.is_dst()
        )

        DT: DateTime
        DT = self.__class__

        d = DT()
        d.COUNTRY_CODE = self.COUNTRY_CODE

        ##* cause UTC, just addition of timedelta from TZ

        # tz: str
        # tz = "UTC"

        # td: str
        # td = self.CTZ.get_td(tzname=tz)

        d.DATETIME = dt.datetime.utcfromtimestamp(tm) + dt.timedelta(milliseconds=s, microseconds=f)
        d.DATETIME = d.DATETIME.replace(tzinfo=self.CTZ.timezone(td_str=self.TIMEDELTA))
        d.DATETIME = d.DATETIME + self.CTZ.timedelta(td_str=self.TIMEDELTA)        
        
        d.TZ_INFO = self.TZ_INFO
        d.TZ_NAME = self.TZ_NAME
        d.TIMEDELTA = self.TIMEDELTA
        
        if hasattr(self, "CTZ"):

            d.CTZ = self.CTZ

        else:

            raise DateTimeInitError(f"{self.__class__.__name__} object has no CTZ attribute.")

        return d

    def get_struct_tm(self: DateTime, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, weekdays: int = 0, yeardays: int = 0, is_dst: int = -1) -> time.struct_time:
        
        years = self.get_year() if years == 0 else years
        months = self.get_month() if months == 0 else months
        days = self.get_day() if days == 0 else days
        hours = self.get_hours() if hours == 0 else hours
        minutes = self.get_minutes() if minutes == 0 else minutes
        seconds = self.get_seconds() if seconds == 0 else seconds
        weekdays = self.get_weekday(years=years, months=months, days=days) if weekdays == 0 else weekdays
        yeardays = self.get_yearday(years=years, months=months, days=days) if yeardays == 0 else yeardays
        is_dst = self.is_dst() if is_dst == -1 else is_dst

        return time.mktime((
            years,
            months,
            days,
            hours,
            minutes,
            seconds,
            weekdays,
            yeardays,
            is_dst
        ))

    def get_year(self: DateTime) -> int:

        return self.DATETIME.year

    def get_month(self: DateTime) -> int:

        return self.DATETIME.month

    ##* get max days in month
    def get_mon(self: DateTime, years: int = 0, months: int = 0) -> int:

        years = self.get_year() if years == 0 else years
        months = self.get_month() if months == 0 else months

        if months == 1: return 31

        if months == 2: return (28 if years % 400 and not (years % 100) else 29) if not years % 4 else 28

        ##* start at march
        if months <= 12:

            ##* 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
            ##* 31, 30, 31, 30, 31
            ##* 31, 30
        
            # return (31, 30, 31, 30, 31).__getitem__((months - 3) % 5)

            k: int

            ##* start at march
            k = (months - 3) % 5
            # k = k + 1

            ##* odd is 31 and even is 30
            # return 31 if k & 1 else 30
            return 31 if not k & 1 else 30

        raise DateTimeInitError(f"Invalid month")

    def get_weekday(self: DateTime, years: int = 0, months: int = 0, days: int = 0) -> int:

        years = self.get_year() if years == 0 else years
        months = self.get_month() if months == 0 else months
        days = self.get_day() if days == 0 else days

        ##* same fast way
        # return dt.datetime(years, months, days).weekday()

        ##* 365 default, 28 + 337, 337 is constant
        ##* start at 1900, 1, 1
        ##* (1900, years - 1) + yearday
        ##* self.get_yearday(years=1900,months=12,days=31)
        ##* if years lt 100 than start_at_years = 1, start_at_wdays=0

        if years < 100:

            return self.__get_weekday(
                years=years,
                months=months,
                days=days,
                start_at_years=1,
                start_at_wdays=0
            )

        ##* pattern per 100 years
        ##* 4, 2, 0, 5

        i: int
        k: int
        k = years // 100

        ##* alternative Modulo
        ##* x % y
        ##* x - ((x // y) * y)
        i = (k - 1) % 4
        # i = k - (((k - 1) // 4) * 4) - 1

        w: int
        w = (4, 2, 0, 5).__getitem__(i)

        return self.__get_weekday(
            years=years,
            months=months,
            days=days,
            start_at_years=k * 100,
            start_at_wdays=w
        )
    
    def __get_weekday(self: DateTime, years: int, months: int, days: int, start_at_years: int, start_at_wdays: int) -> int:

        if years < start_at_years:

            raise DateTimeInitError(f"Invalid year")

        Y: int
        Y = 0

        wday: int

        ##* start at monday (index)
        wday = start_at_wdays

        ##* monday 1
        ##* 0 1 2 ...
        ##* sunday monday
        ##* 1 monday
        ##* next year is tuesday

        for Y in range(start_at_years, years):

            yday: int
            yday = self.get_yearday(years=Y, months=12, days=31)

            ##* if yday 366 than wday is equals 2 
            wday += 1 if yday == 365 or not yday != 366 else 2

            wday = wday % 7

        ##* addition in current year
        wday = wday + self.get_yearday(years=years, months=months, days=days)
        wday = wday % 7

        ##* make it zero is monday, and six is sunday
        wday = 6 if wday == 0 else wday - 1

        return wday

    def get_day(self: DateTime) -> int:

        return self.DATETIME.day

    def get_yearday(self: DateTime, years: int = 0, months: int = 0, days: int = 0) -> int:

        years = self.get_year() if years == 0 else years
        months = self.get_month() if months == 0 else months
        days = self.get_day() if days == 0 else days

        z: int
        z = 0

        m: int
        m = 0

        for m in range(1, months):

            z += self.get_mon(years=years, months=m)

        return z + days
        

    def get_hours(self: DateTime) -> int:

        return self.DATETIME.hour

    def get_minutes(self: DateTime) -> int:

        return self.DATETIME.minute

    def get_seconds(self: DateTime) -> int:

        return self.DATETIME.second

    def get_milliseconds(self: DateTime) -> int:
        
        return self.DATETIME.microsecond // 1000

    def get_microseconds(self: DateTime) -> int:

        return self.DATETIME.microsecond

    def is_dst(self: DateTime) -> int:

        return 0


class TimeFix(object):

    MONTH_FULLNAMES: List[str]
    MONTH_FULLNAMES = [ "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december" ]

    MONTH_NAMES: List[str]
    MONTH_NAMES = [ "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec" ]

    ROMAN_NUMS: List[str]
    ROMAN_NUMS = [ "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII" ]

    CTZ: CSVTimeZoneLoaderType

    def __init__(self, tzfile: Union[str, io.TextIOWrapper, io.BytesIO, io.StringIO, tempfile._TemporaryFileWrapper, None] = None) -> None:

        if not tzfile: 
        
            self.CTZ = CSVTimeZoneLoader(tzfile=io.BytesIO(b"AD,CEST,Europe/Andorra,+0200\nAG,AST,America/Antigua,-0400\nAI,AST,America/Anguilla,-0400\nAL,CEST,Europe/Tirane,+0200\nAO,WAT,Africa/Luanda,+0100\nAQ,NZST,Antarctica/McMurdo,+1200\nAT,CEST,Europe/Vienna,+0200\nAU,ACST,Australia/Adelaide,+0930\nAU,ACST,Australia/Broken_Hill,+0930\nAU,ACST,Australia/Darwin,+0930\nAU,AEST,Antarctica/Macquarie,+1000\nAU,AEST,Australia/Brisbane,+1000\nAU,AEST,Australia/Hobart,+1000\nAU,AEST,Australia/Lindeman,+1000\nAU,AEST,Australia/Melbourne,+1000\nAU,AEST,Australia/Sydney,+1000\nAU,AWST,Australia/Perth,+0800\nAW,AST,America/Aruba,-0400\nAX,EEST,Europe/Mariehamn,+0300\nBA,CEST,Europe/Sarajevo,+0200\nBB,AST,America/Barbados,-0400\nBE,CEST,Europe/Brussels,+0200\nBF,GMT,Africa/Ouagadougou,+0000\nBG,EEST,Europe/Sofia,+0300\nBI,CAT,Africa/Bujumbura,+0200\nBJ,WAT,Africa/Porto_Novo,+0100\nBL,AST,America/St_Barthelemy,-0400\nBQ,AST,America/Kralendijk,-0400\nBR,CDT,America/Bahia,-0500\nBS,EDT,America/Nassau,-0400\nBW,CAT,Africa/Gaborone,+0200\nBZ,CST,America/Belize,-0600\nCA,ADT,America/Glace_Bay,-0300\nCA,ADT,America/Goose_Bay,-0300\nCA,ADT,America/Halifax,-0300\nCA,ADT,America/Moncton,-0300\nCA,AST,America/Blanc_Sablon,-0400\nCA,CDT,America/Rainy_River,-0500\nCA,CDT,America/Rankin_Inlet,-0500\nCA,CDT,America/Resolute,-0500\nCA,CDT,America/Winnipeg,-0500\nCA,CST,America/Regina,-0600\nCA,CST,America/Swift_Current,-0600\nCA,EDT,America/Iqaluit,-0400\nCA,EDT,America/Nipigon,-0400\nCA,EDT,America/Pangnirtung,-0400\nCA,EDT,America/Thunder_Bay,-0400\nCA,EDT,America/Toronto,-0400\nCA,EST,America/Atikokan,-0500\nCA,MDT,America/Cambridge_Bay,-0600\nCA,MDT,America/Edmonton,-0600\nCA,MDT,America/Inuvik,-0600\nCA,MDT,America/Yellowknife,-0600\nCA,MST,America/Creston,-0700\nCA,MST,America/Dawson,-0700\nCA,MST,America/Dawson_Creek,-0700\nCA,MST,America/Fort_Nelson,-0700\nCA,MST,America/Whitehorse,-0700\nCA,NDT,America/St_Johns,-0230\nCA,PDT,America/Vancouver,-0700\nCD,CAT,Africa/Lubumbashi,+0200\nCD,WAT,Africa/Kinshasa,+0100\nCF,WAT,Africa/Bangui,+0100\nCG,WAT,Africa/Brazzaville,+0100\nCH,CEST,Europe/Zurich,+0200\nCI,GMT,Africa/Abidjan,+0000\nCM,WAT,Africa/Douala,+0100\nCN,CST,Asia/Shanghai,+0800\nCR,CST,America/Costa_Rica,-0600\nCU,CDT,America/Havana,-0400\nCW,AST,America/Curacao,-0400\nCY,EEST,Asia/Famagusta,+0300\nCY,EEST,Asia/Nicosia,+0300\nCZ,CEST,Europe/Prague,+0200\nDE,CEST,Europe/Berlin,+0200\nDE,CEST,Europe/Busingen,+0200\nDJ,EAT,Africa/Djibouti,+0300\nDK,CEST,Europe/Copenhagen,+0200\nDM,AST,America/Dominica,-0400\nDO,AST,America/Santo_Domingo,-0400\nDZ,CET,Africa/Algiers,+0100\nEE,EEST,Europe/Tallinn,+0300\nEG,EET,Africa/Cairo,+0200\nER,EAT,Africa/Asmara,+0300\nES,CEST,Africa/Ceuta,+0200\nES,CEST,Europe/Madrid,+0200\nET,EAT,Africa/Addis_Ababa,+0300\nFI,EEST,Europe/Helsinki,+0300\nFR,CEST,Europe/Paris,+0200\nGA,WAT,Africa/Libreville,+0100\nGB,BST,Europe/London,+0100\nGD,AST,America/Grenada,-0400\nGG,BST,Europe/Guernsey,+0100\nGH,GMT,Africa/Accra,+0000\nGI,CEST,Europe/Gibraltar,+0200\nGL,ADT,America/Thule,-0300\nGL,GMT,America/Danmarkshavn,+0000\nGM,GMT,Africa/Banjul,+0000\nGN,GMT,Africa/Conakry,+0000\nGP,AST,America/Guadeloupe,-0400\nGQ,WAT,Africa/Malabo,+0100\nGR,EEST,Europe/Athens,+0300\nGT,CST,America/Guatemala,-0600\nGW,GMT,Africa/Bissau,+0000\nHK,HKT,Asia/Hong_Kong,+0800\nHN,CST,America/Tegucigalpa,-0600\nHR,CEST,Europe/Zagreb,+0200\nHT,EDT,America/Port_au_Prince,-0400\nHU,CEST,Europe/Budapest,+0200\nID,WIB,Asia/Jakarta,+0700\nID,WIB,Asia/Pontianak,+0700\nID,WITA,Asia/Makassar,+0800\nID,WIT,Asia/Jayapura,+0900\nIE,IST,Europe/Dublin,+0100\nIL,IDT,Asia/Jerusalem,+0300\nIM,BST,Europe/Isle_of_Man,+0100\nIN,IST,Asia/Kolkata,+0530\nIT,CEST,Europe/Rome,+0200\nJE,BST,Europe/Jersey,+0100\nJM,EST,America/Jamaica,-0500\nJO,EEST,Asia/Amman,+0300\nJP,JST,Asia/Tokyo,+0900\nKE,EAT,Africa/Nairobi,+0300\nKN,AST,America/St_Kitts,-0400\nKP,KST,Asia/Pyongyang,+0900\nKR,KST,Asia/Seoul,+0900\nKY,EST,America/Cayman,-0500\nLB,EEST,Asia/Beirut,+0300\nLC,AST,America/St_Lucia,-0400\nLI,CEST,Europe/Vaduz,+0200\nLR,GMT,Africa/Monrovia,+0000\nLS,SAST,Africa/Maseru,+0200\nLT,EEST,Europe/Vilnius,+0300\nLU,CEST,Europe/Luxembourg,+0200\nLV,EEST,Europe/Riga,+0300\nLY,EET,Africa/Tripoli,+0200\nMC,CEST,Europe/Monaco,+0200\nMD,EEST,Europe/Chisinau,+0300\nME,CEST,Europe/Podgorica,+0200\nMF,AST,America/Marigot,-0400\nMK,CEST,Europe/Skopje,+0200\nML,GMT,Africa/Bamako,+0000\nMO,CST,Asia/Macau,+0800\nMQ,AST,America/Martinique,-0400\nMR,GMT,Africa/Nouakchott,+0000\nMS,AST,America/Montserrat,-0400\nMT,CEST,Europe/Malta,+0200\nMW,CAT,Africa/Blantyre,+0200\nMX,CDT,America/Bahia_Banderas,-0500\nMX,CDT,America/Matamoros,-0500\nMX,CDT,America/Merida,-0500\nMX,CDT,America/Mexico_City,-0500\nMX,CDT,America/Monterrey,-0500\nMX,EST,America/Cancun,-0500\nMX,MDT,America/Chihuahua,-0600\nMX,MDT,America/Mazatlan,-0600\nMX,MDT,America/Ojinaga,-0600\nMX,MST,America/Hermosillo,-0700\nMX,PDT,America/Tijuana,-0700\nMZ,CAT,Africa/Maputo,+0200\nNA,CAT,Africa/Windhoek,+0200\nNE,WAT,Africa/Niamey,+0100\nNG,WAT,Africa/Lagos,+0100\nNI,CST,America/Managua,-0600\nNL,CEST,Europe/Amsterdam,+0200\nNO,CEST,Europe/Oslo,+0200\nPA,EST,America/Panama,-0500\nPH,PST,Asia/Manila,+0800\nPK,PKT,Asia/Karachi,+0500\nPL,CEST,Europe/Warsaw,+0200\nPR,AST,America/Puerto_Rico,-0400\nPS,EEST,Asia/Gaza,+0300\nPS,EEST,Asia/Hebron,+0300\nPT,WEST,Europe/Lisbon,+0100\nRO,EEST,Europe/Bucharest,+0300\nRS,CEST,Europe/Belgrade,+0200\nRU,EET,Europe/Kaliningrad,+0200\nRU,MSK,Europe/Moscow,+0300\nRW,CAT,Africa/Kigali,+0200\nSD,CAT,Africa/Khartoum,+0200\nSE,CEST,Europe/Stockholm,+0200\nSI,CEST,Europe/Ljubljana,+0200\nSK,CEST,Europe/Bratislava,+0200\nSL,GMT,Africa/Freetown,+0000\nSM,CEST,Europe/San_Marino,+0200\nSN,GMT,Africa/Dakar,+0000\nSO,EAT,Africa/Mogadishu,+0300\nSS,CAT,Africa/Juba,+0200\nST,GMT,Africa/Sao_Tome,+0000\nSV,CST,America/El_Salvador,-0600\nSX,AST,America/Lower_Princes,-0400\nSY,EEST,Asia/Damascus,+0300\nSZ,SAST,Africa/Mbabane,+0200\nTC,EDT,America/Grand_Turk,-0400\nTD,WAT,Africa/Ndjamena,+0100\nTG,GMT,Africa/Lome,+0000\nTN,CET,Africa/Tunis,+0100\nTT,AST,America/Port_of_Spain,-0400\nTW,CST,Asia/Taipei,+0800\nTZ,EAT,Africa/Dar_es_Salaam,+0300\nUA,EEST,Europe/Kiev,+0300\nUA,EEST,Europe/Uzhgorod,+0300\nUA,EEST,Europe/Zaporozhye,+0300\nUA,MSK,Europe/Simferopol,+0300\nUG,EAT,Africa/Kampala,+0300\nUS,AKDT,America/Anchorage,-0800\nUS,AKDT,America/Juneau,-0800\nUS,AKDT,America/Metlakatla,-0800\nUS,AKDT,America/Nome,-0800\nUS,AKDT,America/Sitka,-0800\nUS,AKDT,America/Yakutat,-0800\nUS,CDT,America/Chicago,-0500\nUS,CDT,America/Menominee,-0500\nUS,EDT,America/Detroit,-0400\nUS,EDT,America/New_York,-0400\nUS,HDT,America/Adak,-0900\nUS,MDT,America/Boise,-0600\nUS,MDT,America/Denver,-0600\nUS,MST,America/Phoenix,-0700\nUS,PDT,America/Los_Angeles,-0700\nVA,CEST,Europe/Vatican,+0200\nVC,AST,America/St_Vincent,-0400\nVG,AST,America/Tortola,-0400\nVI,AST,America/St_Thomas,-0400\nZA,SAST,Africa/Johannesburg,+0200\nZM,CAT,Africa/Lusaka,+0200\nZW,CAT,Africa/Harare,+0200"))
        
        else:

            self.CTZ = CSVTimeZoneLoader(tzfile=tzfile)


if str(__name__).upper() in ("__MAIN__",):

    # with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", prefix="tz_", dir=None, delete=True) as t:

    #     ##* GMT, UTC +0000
        
    #     t.write("AD,CEST,Europe/Andorra,+0200\nAG,AST,America/Antigua,-0400\nAI,AST,America/Anguilla,-0400\nAL,CEST,Europe/Tirane,+0200\nAO,WAT,Africa/Luanda,+0100\nAQ,NZST,Antarctica/McMurdo,+1200\nAT,CEST,Europe/Vienna,+0200\nAU,ACST,Australia/Adelaide,+0930\nAU,ACST,Australia/Broken_Hill,+0930\nAU,ACST,Australia/Darwin,+0930\nAU,AEST,Antarctica/Macquarie,+1000\nAU,AEST,Australia/Brisbane,+1000\nAU,AEST,Australia/Hobart,+1000\nAU,AEST,Australia/Lindeman,+1000\nAU,AEST,Australia/Melbourne,+1000\nAU,AEST,Australia/Sydney,+1000\nAU,AWST,Australia/Perth,+0800\nAW,AST,America/Aruba,-0400\nAX,EEST,Europe/Mariehamn,+0300\nBA,CEST,Europe/Sarajevo,+0200\nBB,AST,America/Barbados,-0400\nBE,CEST,Europe/Brussels,+0200\nBF,GMT,Africa/Ouagadougou,+0000\nBG,EEST,Europe/Sofia,+0300\nBI,CAT,Africa/Bujumbura,+0200\nBJ,WAT,Africa/Porto_Novo,+0100\nBL,AST,America/St_Barthelemy,-0400\nBQ,AST,America/Kralendijk,-0400\nBR,CDT,America/Bahia,-0500\nBS,EDT,America/Nassau,-0400\nBW,CAT,Africa/Gaborone,+0200\nBZ,CST,America/Belize,-0600\nCA,ADT,America/Glace_Bay,-0300\nCA,ADT,America/Goose_Bay,-0300\nCA,ADT,America/Halifax,-0300\nCA,ADT,America/Moncton,-0300\nCA,AST,America/Blanc_Sablon,-0400\nCA,CDT,America/Rainy_River,-0500\nCA,CDT,America/Rankin_Inlet,-0500\nCA,CDT,America/Resolute,-0500\nCA,CDT,America/Winnipeg,-0500\nCA,CST,America/Regina,-0600\nCA,CST,America/Swift_Current,-0600\nCA,EDT,America/Iqaluit,-0400\nCA,EDT,America/Nipigon,-0400\nCA,EDT,America/Pangnirtung,-0400\nCA,EDT,America/Thunder_Bay,-0400\nCA,EDT,America/Toronto,-0400\nCA,EST,America/Atikokan,-0500\nCA,MDT,America/Cambridge_Bay,-0600\nCA,MDT,America/Edmonton,-0600\nCA,MDT,America/Inuvik,-0600\nCA,MDT,America/Yellowknife,-0600\nCA,MST,America/Creston,-0700\nCA,MST,America/Dawson,-0700\nCA,MST,America/Dawson_Creek,-0700\nCA,MST,America/Fort_Nelson,-0700\nCA,MST,America/Whitehorse,-0700\nCA,NDT,America/St_Johns,-0230\nCA,PDT,America/Vancouver,-0700\nCD,CAT,Africa/Lubumbashi,+0200\nCD,WAT,Africa/Kinshasa,+0100\nCF,WAT,Africa/Bangui,+0100\nCG,WAT,Africa/Brazzaville,+0100\nCH,CEST,Europe/Zurich,+0200\nCI,GMT,Africa/Abidjan,+0000\nCM,WAT,Africa/Douala,+0100\nCN,CST,Asia/Shanghai,+0800\nCR,CST,America/Costa_Rica,-0600\nCU,CDT,America/Havana,-0400\nCW,AST,America/Curacao,-0400\nCY,EEST,Asia/Famagusta,+0300\nCY,EEST,Asia/Nicosia,+0300\nCZ,CEST,Europe/Prague,+0200\nDE,CEST,Europe/Berlin,+0200\nDE,CEST,Europe/Busingen,+0200\nDJ,EAT,Africa/Djibouti,+0300\nDK,CEST,Europe/Copenhagen,+0200\nDM,AST,America/Dominica,-0400\nDO,AST,America/Santo_Domingo,-0400\nDZ,CET,Africa/Algiers,+0100\nEE,EEST,Europe/Tallinn,+0300\nEG,EET,Africa/Cairo,+0200\nER,EAT,Africa/Asmara,+0300\nES,CEST,Africa/Ceuta,+0200\nES,CEST,Europe/Madrid,+0200\nET,EAT,Africa/Addis_Ababa,+0300\nFI,EEST,Europe/Helsinki,+0300\nFR,CEST,Europe/Paris,+0200\nGA,WAT,Africa/Libreville,+0100\nGB,BST,Europe/London,+0100\nGD,AST,America/Grenada,-0400\nGG,BST,Europe/Guernsey,+0100\nGH,GMT,Africa/Accra,+0000\nGI,CEST,Europe/Gibraltar,+0200\nGL,ADT,America/Thule,-0300\nGL,GMT,America/Danmarkshavn,+0000\nGM,GMT,Africa/Banjul,+0000\nGN,GMT,Africa/Conakry,+0000\nGP,AST,America/Guadeloupe,-0400\nGQ,WAT,Africa/Malabo,+0100\nGR,EEST,Europe/Athens,+0300\nGT,CST,America/Guatemala,-0600\nGW,GMT,Africa/Bissau,+0000\nHK,HKT,Asia/Hong_Kong,+0800\nHN,CST,America/Tegucigalpa,-0600\nHR,CEST,Europe/Zagreb,+0200\nHT,EDT,America/Port_au_Prince,-0400\nHU,CEST,Europe/Budapest,+0200\nID,WIB,Asia/Jakarta,+0700\nID,WIB,Asia/Pontianak,+0700\nID,WITA,Asia/Makassar,+0800\nID,WIT,Asia/Jayapura,+0900\nIE,IST,Europe/Dublin,+0100\nIL,IDT,Asia/Jerusalem,+0300\nIM,BST,Europe/Isle_of_Man,+0100\nIN,IST,Asia/Kolkata,+0530\nIT,CEST,Europe/Rome,+0200\nJE,BST,Europe/Jersey,+0100\nJM,EST,America/Jamaica,-0500\nJO,EEST,Asia/Amman,+0300\nJP,JST,Asia/Tokyo,+0900\nKE,EAT,Africa/Nairobi,+0300\nKN,AST,America/St_Kitts,-0400\nKP,KST,Asia/Pyongyang,+0900\nKR,KST,Asia/Seoul,+0900\nKY,EST,America/Cayman,-0500\nLB,EEST,Asia/Beirut,+0300\nLC,AST,America/St_Lucia,-0400\nLI,CEST,Europe/Vaduz,+0200\nLR,GMT,Africa/Monrovia,+0000\nLS,SAST,Africa/Maseru,+0200\nLT,EEST,Europe/Vilnius,+0300\nLU,CEST,Europe/Luxembourg,+0200\nLV,EEST,Europe/Riga,+0300\nLY,EET,Africa/Tripoli,+0200\nMC,CEST,Europe/Monaco,+0200\nMD,EEST,Europe/Chisinau,+0300\nME,CEST,Europe/Podgorica,+0200\nMF,AST,America/Marigot,-0400\nMK,CEST,Europe/Skopje,+0200\nML,GMT,Africa/Bamako,+0000\nMO,CST,Asia/Macau,+0800\nMQ,AST,America/Martinique,-0400\nMR,GMT,Africa/Nouakchott,+0000\nMS,AST,America/Montserrat,-0400\nMT,CEST,Europe/Malta,+0200\nMW,CAT,Africa/Blantyre,+0200\nMX,CDT,America/Bahia_Banderas,-0500\nMX,CDT,America/Matamoros,-0500\nMX,CDT,America/Merida,-0500\nMX,CDT,America/Mexico_City,-0500\nMX,CDT,America/Monterrey,-0500\nMX,EST,America/Cancun,-0500\nMX,MDT,America/Chihuahua,-0600\nMX,MDT,America/Mazatlan,-0600\nMX,MDT,America/Ojinaga,-0600\nMX,MST,America/Hermosillo,-0700\nMX,PDT,America/Tijuana,-0700\nMZ,CAT,Africa/Maputo,+0200\nNA,CAT,Africa/Windhoek,+0200\nNE,WAT,Africa/Niamey,+0100\nNG,WAT,Africa/Lagos,+0100\nNI,CST,America/Managua,-0600\nNL,CEST,Europe/Amsterdam,+0200\nNO,CEST,Europe/Oslo,+0200\nPA,EST,America/Panama,-0500\nPH,PST,Asia/Manila,+0800\nPK,PKT,Asia/Karachi,+0500\nPL,CEST,Europe/Warsaw,+0200\nPR,AST,America/Puerto_Rico,-0400\nPS,EEST,Asia/Gaza,+0300\nPS,EEST,Asia/Hebron,+0300\nPT,WEST,Europe/Lisbon,+0100\nRO,EEST,Europe/Bucharest,+0300\nRS,CEST,Europe/Belgrade,+0200\nRU,EET,Europe/Kaliningrad,+0200\nRU,MSK,Europe/Moscow,+0300\nRW,CAT,Africa/Kigali,+0200\nSD,CAT,Africa/Khartoum,+0200\nSE,CEST,Europe/Stockholm,+0200\nSI,CEST,Europe/Ljubljana,+0200\nSK,CEST,Europe/Bratislava,+0200\nSL,GMT,Africa/Freetown,+0000\nSM,CEST,Europe/San_Marino,+0200\nSN,GMT,Africa/Dakar,+0000\nSO,EAT,Africa/Mogadishu,+0300\nSS,CAT,Africa/Juba,+0200\nST,GMT,Africa/Sao_Tome,+0000\nSV,CST,America/El_Salvador,-0600\nSX,AST,America/Lower_Princes,-0400\nSY,EEST,Asia/Damascus,+0300\nSZ,SAST,Africa/Mbabane,+0200\nTC,EDT,America/Grand_Turk,-0400\nTD,WAT,Africa/Ndjamena,+0100\nTG,GMT,Africa/Lome,+0000\nTN,CET,Africa/Tunis,+0100\nTT,AST,America/Port_of_Spain,-0400\nTW,CST,Asia/Taipei,+0800\nTZ,EAT,Africa/Dar_es_Salaam,+0300\nUA,EEST,Europe/Kiev,+0300\nUA,EEST,Europe/Uzhgorod,+0300\nUA,EEST,Europe/Zaporozhye,+0300\nUA,MSK,Europe/Simferopol,+0300\nUG,EAT,Africa/Kampala,+0300\nUS,AKDT,America/Anchorage,-0800\nUS,AKDT,America/Juneau,-0800\nUS,AKDT,America/Metlakatla,-0800\nUS,AKDT,America/Nome,-0800\nUS,AKDT,America/Sitka,-0800\nUS,AKDT,America/Yakutat,-0800\nUS,CDT,America/Chicago,-0500\nUS,CDT,America/Menominee,-0500\nUS,EDT,America/Detroit,-0400\nUS,EDT,America/New_York,-0400\nUS,HDT,America/Adak,-0900\nUS,MDT,America/Boise,-0600\nUS,MDT,America/Denver,-0600\nUS,MST,America/Phoenix,-0700\nUS,PDT,America/Los_Angeles,-0700\nVA,CEST,Europe/Vatican,+0200\nVC,AST,America/St_Vincent,-0400\nVG,AST,America/Tortola,-0400\nVI,AST,America/St_Thomas,-0400\nZA,SAST,Africa/Johannesburg,+0200\nZM,CAT,Africa/Lusaka,+0200\nZW,CAT,Africa/Harare,+0200")
    #     t.seek(0)

    #     print(type(d))

    #     print(os.fstat(t.fileno()))
    #     print(t.name)

    ctz = CSVTimeZoneLoader(io.BytesIO(b"AD,CEST,Europe/Andorra,+0200\nAG,AST,America/Antigua,-0400\nAI,AST,America/Anguilla,-0400\nAL,CEST,Europe/Tirane,+0200\nAO,WAT,Africa/Luanda,+0100\nAQ,NZST,Antarctica/McMurdo,+1200\nAT,CEST,Europe/Vienna,+0200\nAU,ACST,Australia/Adelaide,+0930\nAU,ACST,Australia/Broken_Hill,+0930\nAU,ACST,Australia/Darwin,+0930\nAU,AEST,Antarctica/Macquarie,+1000\nAU,AEST,Australia/Brisbane,+1000\nAU,AEST,Australia/Hobart,+1000\nAU,AEST,Australia/Lindeman,+1000\nAU,AEST,Australia/Melbourne,+1000\nAU,AEST,Australia/Sydney,+1000\nAU,AWST,Australia/Perth,+0800\nAW,AST,America/Aruba,-0400\nAX,EEST,Europe/Mariehamn,+0300\nBA,CEST,Europe/Sarajevo,+0200\nBB,AST,America/Barbados,-0400\nBE,CEST,Europe/Brussels,+0200\nBF,GMT,Africa/Ouagadougou,+0000\nBG,EEST,Europe/Sofia,+0300\nBI,CAT,Africa/Bujumbura,+0200\nBJ,WAT,Africa/Porto_Novo,+0100\nBL,AST,America/St_Barthelemy,-0400\nBQ,AST,America/Kralendijk,-0400\nBR,CDT,America/Bahia,-0500\nBS,EDT,America/Nassau,-0400\nBW,CAT,Africa/Gaborone,+0200\nBZ,CST,America/Belize,-0600\nCA,ADT,America/Glace_Bay,-0300\nCA,ADT,America/Goose_Bay,-0300\nCA,ADT,America/Halifax,-0300\nCA,ADT,America/Moncton,-0300\nCA,AST,America/Blanc_Sablon,-0400\nCA,CDT,America/Rainy_River,-0500\nCA,CDT,America/Rankin_Inlet,-0500\nCA,CDT,America/Resolute,-0500\nCA,CDT,America/Winnipeg,-0500\nCA,CST,America/Regina,-0600\nCA,CST,America/Swift_Current,-0600\nCA,EDT,America/Iqaluit,-0400\nCA,EDT,America/Nipigon,-0400\nCA,EDT,America/Pangnirtung,-0400\nCA,EDT,America/Thunder_Bay,-0400\nCA,EDT,America/Toronto,-0400\nCA,EST,America/Atikokan,-0500\nCA,MDT,America/Cambridge_Bay,-0600\nCA,MDT,America/Edmonton,-0600\nCA,MDT,America/Inuvik,-0600\nCA,MDT,America/Yellowknife,-0600\nCA,MST,America/Creston,-0700\nCA,MST,America/Dawson,-0700\nCA,MST,America/Dawson_Creek,-0700\nCA,MST,America/Fort_Nelson,-0700\nCA,MST,America/Whitehorse,-0700\nCA,NDT,America/St_Johns,-0230\nCA,PDT,America/Vancouver,-0700\nCD,CAT,Africa/Lubumbashi,+0200\nCD,WAT,Africa/Kinshasa,+0100\nCF,WAT,Africa/Bangui,+0100\nCG,WAT,Africa/Brazzaville,+0100\nCH,CEST,Europe/Zurich,+0200\nCI,GMT,Africa/Abidjan,+0000\nCM,WAT,Africa/Douala,+0100\nCN,CST,Asia/Shanghai,+0800\nCR,CST,America/Costa_Rica,-0600\nCU,CDT,America/Havana,-0400\nCW,AST,America/Curacao,-0400\nCY,EEST,Asia/Famagusta,+0300\nCY,EEST,Asia/Nicosia,+0300\nCZ,CEST,Europe/Prague,+0200\nDE,CEST,Europe/Berlin,+0200\nDE,CEST,Europe/Busingen,+0200\nDJ,EAT,Africa/Djibouti,+0300\nDK,CEST,Europe/Copenhagen,+0200\nDM,AST,America/Dominica,-0400\nDO,AST,America/Santo_Domingo,-0400\nDZ,CET,Africa/Algiers,+0100\nEE,EEST,Europe/Tallinn,+0300\nEG,EET,Africa/Cairo,+0200\nER,EAT,Africa/Asmara,+0300\nES,CEST,Africa/Ceuta,+0200\nES,CEST,Europe/Madrid,+0200\nET,EAT,Africa/Addis_Ababa,+0300\nFI,EEST,Europe/Helsinki,+0300\nFR,CEST,Europe/Paris,+0200\nGA,WAT,Africa/Libreville,+0100\nGB,BST,Europe/London,+0100\nGD,AST,America/Grenada,-0400\nGG,BST,Europe/Guernsey,+0100\nGH,GMT,Africa/Accra,+0000\nGI,CEST,Europe/Gibraltar,+0200\nGL,ADT,America/Thule,-0300\nGL,GMT,America/Danmarkshavn,+0000\nGM,GMT,Africa/Banjul,+0000\nGN,GMT,Africa/Conakry,+0000\nGP,AST,America/Guadeloupe,-0400\nGQ,WAT,Africa/Malabo,+0100\nGR,EEST,Europe/Athens,+0300\nGT,CST,America/Guatemala,-0600\nGW,GMT,Africa/Bissau,+0000\nHK,HKT,Asia/Hong_Kong,+0800\nHN,CST,America/Tegucigalpa,-0600\nHR,CEST,Europe/Zagreb,+0200\nHT,EDT,America/Port_au_Prince,-0400\nHU,CEST,Europe/Budapest,+0200\nID,WIB,Asia/Jakarta,+0700\nID,WIB,Asia/Pontianak,+0700\nID,WITA,Asia/Makassar,+0800\nID,WIT,Asia/Jayapura,+0900\nIE,IST,Europe/Dublin,+0100\nIL,IDT,Asia/Jerusalem,+0300\nIM,BST,Europe/Isle_of_Man,+0100\nIN,IST,Asia/Kolkata,+0530\nIT,CEST,Europe/Rome,+0200\nJE,BST,Europe/Jersey,+0100\nJM,EST,America/Jamaica,-0500\nJO,EEST,Asia/Amman,+0300\nJP,JST,Asia/Tokyo,+0900\nKE,EAT,Africa/Nairobi,+0300\nKN,AST,America/St_Kitts,-0400\nKP,KST,Asia/Pyongyang,+0900\nKR,KST,Asia/Seoul,+0900\nKY,EST,America/Cayman,-0500\nLB,EEST,Asia/Beirut,+0300\nLC,AST,America/St_Lucia,-0400\nLI,CEST,Europe/Vaduz,+0200\nLR,GMT,Africa/Monrovia,+0000\nLS,SAST,Africa/Maseru,+0200\nLT,EEST,Europe/Vilnius,+0300\nLU,CEST,Europe/Luxembourg,+0200\nLV,EEST,Europe/Riga,+0300\nLY,EET,Africa/Tripoli,+0200\nMC,CEST,Europe/Monaco,+0200\nMD,EEST,Europe/Chisinau,+0300\nME,CEST,Europe/Podgorica,+0200\nMF,AST,America/Marigot,-0400\nMK,CEST,Europe/Skopje,+0200\nML,GMT,Africa/Bamako,+0000\nMO,CST,Asia/Macau,+0800\nMQ,AST,America/Martinique,-0400\nMR,GMT,Africa/Nouakchott,+0000\nMS,AST,America/Montserrat,-0400\nMT,CEST,Europe/Malta,+0200\nMW,CAT,Africa/Blantyre,+0200\nMX,CDT,America/Bahia_Banderas,-0500\nMX,CDT,America/Matamoros,-0500\nMX,CDT,America/Merida,-0500\nMX,CDT,America/Mexico_City,-0500\nMX,CDT,America/Monterrey,-0500\nMX,EST,America/Cancun,-0500\nMX,MDT,America/Chihuahua,-0600\nMX,MDT,America/Mazatlan,-0600\nMX,MDT,America/Ojinaga,-0600\nMX,MST,America/Hermosillo,-0700\nMX,PDT,America/Tijuana,-0700\nMZ,CAT,Africa/Maputo,+0200\nNA,CAT,Africa/Windhoek,+0200\nNE,WAT,Africa/Niamey,+0100\nNG,WAT,Africa/Lagos,+0100\nNI,CST,America/Managua,-0600\nNL,CEST,Europe/Amsterdam,+0200\nNO,CEST,Europe/Oslo,+0200\nPA,EST,America/Panama,-0500\nPH,PST,Asia/Manila,+0800\nPK,PKT,Asia/Karachi,+0500\nPL,CEST,Europe/Warsaw,+0200\nPR,AST,America/Puerto_Rico,-0400\nPS,EEST,Asia/Gaza,+0300\nPS,EEST,Asia/Hebron,+0300\nPT,WEST,Europe/Lisbon,+0100\nRO,EEST,Europe/Bucharest,+0300\nRS,CEST,Europe/Belgrade,+0200\nRU,EET,Europe/Kaliningrad,+0200\nRU,MSK,Europe/Moscow,+0300\nRW,CAT,Africa/Kigali,+0200\nSD,CAT,Africa/Khartoum,+0200\nSE,CEST,Europe/Stockholm,+0200\nSI,CEST,Europe/Ljubljana,+0200\nSK,CEST,Europe/Bratislava,+0200\nSL,GMT,Africa/Freetown,+0000\nSM,CEST,Europe/San_Marino,+0200\nSN,GMT,Africa/Dakar,+0000\nSO,EAT,Africa/Mogadishu,+0300\nSS,CAT,Africa/Juba,+0200\nST,GMT,Africa/Sao_Tome,+0000\nSV,CST,America/El_Salvador,-0600\nSX,AST,America/Lower_Princes,-0400\nSY,EEST,Asia/Damascus,+0300\nSZ,SAST,Africa/Mbabane,+0200\nTC,EDT,America/Grand_Turk,-0400\nTD,WAT,Africa/Ndjamena,+0100\nTG,GMT,Africa/Lome,+0000\nTN,CET,Africa/Tunis,+0100\nTT,AST,America/Port_of_Spain,-0400\nTW,CST,Asia/Taipei,+0800\nTZ,EAT,Africa/Dar_es_Salaam,+0300\nUA,EEST,Europe/Kiev,+0300\nUA,EEST,Europe/Uzhgorod,+0300\nUA,EEST,Europe/Zaporozhye,+0300\nUA,MSK,Europe/Simferopol,+0300\nUG,EAT,Africa/Kampala,+0300\nUS,AKDT,America/Anchorage,-0800\nUS,AKDT,America/Juneau,-0800\nUS,AKDT,America/Metlakatla,-0800\nUS,AKDT,America/Nome,-0800\nUS,AKDT,America/Sitka,-0800\nUS,AKDT,America/Yakutat,-0800\nUS,CDT,America/Chicago,-0500\nUS,CDT,America/Menominee,-0500\nUS,EDT,America/Detroit,-0400\nUS,EDT,America/New_York,-0400\nUS,HDT,America/Adak,-0900\nUS,MDT,America/Boise,-0600\nUS,MDT,America/Denver,-0600\nUS,MST,America/Phoenix,-0700\nUS,PDT,America/Los_Angeles,-0700\nVA,CEST,Europe/Vatican,+0200\nVC,AST,America/St_Vincent,-0400\nVG,AST,America/Tortola,-0400\nVI,AST,America/St_Thomas,-0400\nZA,SAST,Africa/Johannesburg,+0200\nZM,CAT,Africa/Lusaka,+0200\nZW,CAT,Africa/Harare,+0200"))

    # print(ctz.TZ_TABLE_DATA)

    tzinfo = "America/New_York"

    print(dt.datetime.now(tz=dt.timezone.utc))

    d = dt.datetime.now(tz=ctz.timezone(ctz.get_td(tzinfo=tzinfo)))

    print(d)
    print(d.tzinfo)

    print(ctz.get_td(country_code="ID", tzname="WiB"))

    d = d.replace(tzinfo=ctz.timezone(ctz.get_td(tzinfo="Asia/Jakarta", tzname="WiB"))) \
        + ctz.timedelta(ctz.get_td(tzinfo="Asia/Jakarta")) \
            - ctz.timedelta(ctz.get_td(tzinfo=tzinfo))

    print(d)
    print(d.tzinfo)

    d = DateTime()
    d.set_ctz(ctz)
    print(str(d.enhance_tm_sec(0)))

    print("Asia/Jakarta")

    d = DateTime()
    d.set_ctz(ctz)
    print(repr(d.enhance_tm_sec(0)))
    d.DATETIME = d.to_dt(ctz.get_td(tzinfo="Asia/Jakarta"))
    d.ch_dt_from(d.DATETIME) ##* go back to UTC
    print(repr(d.enhance_tm_sec(0)))
    d.DATETIME = d.to_dt(ctz.get_td(tzinfo="Asia/Jakarta"))
    d.COUNTRY_CODE = "ID"
    d.TZ_INFO = "Asia/Jakarta"
    d.TZ_NAME = "WIB"
    d.TIMEDELTA = ctz.get_td(tzinfo="Asia/Jakarta")
    print(repr(d.enhance_tm_sec(0)), "bruh")
    print(repr(d.enhance_tm_sec(3600)))
    print(str(d.enhance_tm_sec(3600)))
    print(repr(d.enhance_tm_ms(0)), "bruh")
    print(repr(d.enhance_tm_ms(9293342998)))
    print(str(d.enhance_tm_ms(9293342998)))
    print(repr(d.enhance_tm_us(0)), "bruh")
    print(repr(d.enhance_tm_us(9293342998)))
    print(str(d.enhance_tm_us(9293342998)))
    # print(d.date_fix(years=2016, months=13,days=45))

    print(str(d.enhance_tm_sec(0)))
    print(str(d.enhance_tm_sec(0).DATETIME.tzname()))

    print(d.get_weekday(years=2022, months=5, days=17))

    print(d.str_to_dt("2022-05-17 18:58:47.342998+0700"))
