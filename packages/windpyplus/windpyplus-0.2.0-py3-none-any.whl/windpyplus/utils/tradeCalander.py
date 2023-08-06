import datetime
import pandas as pd

from WindPy import *
w.start()
   
"""_summary_
# 取上交所2018年5月13日至6月13日的交易日期序列，交易所为空默认为上交所
date_list=w.tdays("2018-05-13", "2018-06-13"," ")
date_list

# 取从今天往前推10个月的日历日
import datetime
today = datetime.date.today() 
w.tdaysoffset(-10, today.isoformat(), "Period=M;Days=Alldays")

# 取从今天往前推10个月的日历日
import datetime
today = datetime.date.today() 
w.tdaysoffset(-10, today.isoformat(), "Period=M;Days=Alldays")

# 统计2018年交易日天数
days=w.tdayscount("2018-01-01", "2018-12-31", "").Data[0]
days

# 用日期宏IPO的示例，获取股票600039.SH上市首日至20180611的收盘价
error_code,data=w.wsd("600039.SH", "close", 'IPO', "2018-06-11", usedf=True)
data.head()
# 用日期宏本月初的示例，获取000001.SZ本月初至20180611的收盘价
from datetime import datetime
td = datetime.today().strftime("%Y%m%d")
error_code,data=w.wsd("600039.SH", "close", 'RMF', td, usedf=True)
data

特殊日期宏
宏名称	助记符	宏名称	助记符	宏名称	助记符
截止日期	ED	今年一季	RQ1	本月初	RMF
开始日期	SD	今年二季	RQ2	本周一	RWF
去年一季	LQ1	今年三季	RQ3	上周末	LWE
去年二季	LQ2	最新一期	MRQ	上月末	LME
去年三季	LQ3	本年初	RYF	上半年末	LHYE
去年年报	LYR	下半年初	RHYF	上年末	LYE
上市首日	IPO	--	--	--	--

"""

def trade_date_sse(star_date='2015-01 -1', end_date='2025-12-31'):
    data = w.tdays(star_date, end_date, options="")
    if data.ErrorCode == 0:
        return data.Data[0]
    else:
        print("error")
        

if __name__ == "__main__":
    print(trade_date_sse()[:5])
    print(trade_date_sse()[-5: ])
    