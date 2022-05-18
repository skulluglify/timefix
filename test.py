#!/usr/bin/env python

import time
import timefix as tm

if str(__name__).upper() in ("__MAIN__",):

    # a = TimeFix.create_dt("2002-07-07Z")
    a = tm.TimeFix.create_dt(time.time())
    # a = TimeFix.create_dt(dt.datetime.now(tz=dt.timezone.utc))

    print(a)

    print(tm.TimeFix.get_months(a))
    print(tm.TimeFix.get_weekdays(a))

    tm.TimeFix.enhance_tm_ms(a, 36000)

    print("H:", a.get_hours())
    print("M:", a.get_minutes())
    print("S:", a.get_seconds())
