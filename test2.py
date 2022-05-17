#!/usr/bin/env python

import os, csv

if str(__name__).upper() in ("__MAIN__",):


    with open("_tz.csv", "r") as f:

        print(f.name)
        print(os.fstat(f.fileno()).st_size)

        c: csv.DictReader
        c = csv.DictReader(
            f=f,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            fieldnames=["country_code","timezone","region","timedelta"],
            restkey=None,
            restval=None
        )

        for row in c:
            print(row["country_code"])

        