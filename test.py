#!/usr/bin/env python

import datetime as dt
import pytz as tz

if str(__name__).upper() in ("__MAIN__",):

    current_tz = tz.country_timezones.get("ID").pop(0)
    utctime = dt.datetime.now(dt.timezone.utc)

    print(utctime.astimezone(tz=tz.timezone(current_tz)))
