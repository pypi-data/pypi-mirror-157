from WindPy import w
from datetime import datetime
import sqlite3

# Connect to the database
conn = sqlite3.connect("example.db")
c = conn.cursor()

# Create an empty table
table_names = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
c.execute("DROP TABLE IF EXISTS stockprice")

c.execute("""
CREATE TABLE stockprice (
    windcode VARCHAR(20) NOT NULL,
    tradedate VARCHAR(50),
    openprice FLOAT,
    highprice FLOAT,
    lowprice FLOAT,
    closeprice FLOAT,
    volume FLOAT,
    amt FLOAT
    )
    """)

sql = "INSERT INTO stockprice VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

w.start()

# Download the changes in the constituents and hisotrical constituents
windcodes_change = w.wset("indexhistory","startdate=2020-01-01;enddate=2020-02-01;windcode=000300.SH;field=tradedate,tradecode")
assert windcodes_change.ErrorCode == 0, 'Download constituents changes, ErrorCode: {0}'.format(windcodes_change.ErrorCode)
windcodes_2015 = w.wset("sectorconstituent","date=2015-01-01;windcode=000300.SH;field=wind_code")
assert windcodes_2015.ErrorCode == 0, 'Download historical constituents, ErrorCode: {0}'.format(windcodes_2015.ErrorCode)

windcodes = list(set(windcodes_change.Data[1] + windcodes_2015.Data[0]))

# Fetch data and save in the database
for windcode in windcodes:
    data = w.wsd(windcode, "open,high,low,close,volume,amt", "IPO", "2019-01-01", "industryType=2;industryStandard=1")

    if data.ErrorCode != 0:
        print(windcode, ":ErrorCode:", data.ErrorCode)
        continue

    for i, date in enumerate(data.Times):
        sqlrow = list()
        for j, field in enumerate(data.Fields):
            sqlrow.append(data.Data[j][i])
        c.execute(sql, [(windcode), (date)] + sqlrow)
    conn.commit()

conn.close()