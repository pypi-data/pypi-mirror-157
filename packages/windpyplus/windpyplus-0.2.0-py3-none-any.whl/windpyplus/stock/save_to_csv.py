from WindPy import w
from datetime import datetime
import pandas as pd

w.start()

# Download the latest constituents of HS300 index
today = datetime.today().strftime('%Y-%m-%d')
windcodes = w.wset("sectorconstituent","date={0};windcode=000300.SH;field=wind_code".format(today))
assert windcodes.ErrorCode == 0, 'Download historical constituents, ErrorCode: {0}'.format(windcodes.ErrorCode)


# Fetch the data of the last 12 months and return a dataframe
dataset = pd.DataFrame(columns=['WINDCODE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'AMT'])
for windcode in windcodes.Data[0]:
    errorcode, data = w.wsd(windcode, "open,high,low,close,volume,amt", "-5D", today, "industryType=2;industryStandard=1", usedf=True)

    if errorcode != 0:
        print(windcode, ":ErrorCode:", errorcode)
        continue

    data.loc[:, 'WINDCODE'] = windcode
    dataset = dataset.append(data, sort=False)

dataset.index.name = 'DATE'
dataset.to_csv('D:/Stock/wind/HS300 Data.csv')