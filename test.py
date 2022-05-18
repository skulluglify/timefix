#!/usr/bin/env python

import time
import timefix as tm

if str(__name__).upper() in ("__MAIN__",):

    # a = tm.TimeFix.create_dt("2002-07-07Z")
    # a = tm.TimeFix.create_dt(time.time())

    print(tm.TimeFix.create_dt("2002-07-07Z"))

    a: tm.DateTimeType
    a = tm.TimeFix.create_dt(tzname="WIB")

    print(a)
    print(a.TZ_INFO)
    print(a.TZ_NAME)
    print(a.TIMEDELTA)

    print(a.to_dt(td_str=tm.TimeFix.CTZ.get_td(tzname="BST")))

    print(tm.TimeFix.get_months(a))
    print(tm.TimeFix.get_weekdays(a))

    tm.TimeFix.enhance_tm_ms(a, 36000)

    print("H:", a.get_hours())
    print("M:", a.get_minutes())
    print("S:", a.get_seconds())
