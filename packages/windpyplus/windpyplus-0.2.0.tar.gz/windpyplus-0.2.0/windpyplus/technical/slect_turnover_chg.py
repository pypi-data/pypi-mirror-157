import code
from WindPy import *
from datetime import *
import pandas as pd
w.start()

# 定义API报错函数
def verifyResult(errCode):
    assert errCode == 0, "API数据提取错误，ErrorCode={}，具体含义请至帮助文档附件《常见API错误码》中查询。".format(errCode)

date =  w.tdaysoffset(-1,datetime.today() , "")
print(verifyResult(date.ErrorCode))
end_Date =  date.Times[0].strftime("%Y%m%d")  #设置时间为上一个交易日，并转化时间格式
print(end_Date)
codes = w.wset("sectorconstituent","date="+end_Date+";sectorid=a001010100000000")
verifyResult(codes.ErrorCode)
code_list = codes.Data[1]   #所有A股 为股票池
print(len(code_list))

error,data = w.wss(code_list,"turn","tradeDate="+end_Date+";priceAdj=U;unit=1;gRateType=1",usedf=True)
verifyResult(error)     #下载截面数据        
    
data = data.fillna(0)                       #缺失设置为0
data = data[data['TURN']!=0]                #因子TURN为缺失的记录删除

data = data.sort_values('TURN')              #截面按因子TURN排序 注意是 由小到大的排序

result = data[-(round(len(data)/10)):]     #选择最后10%的股票 即因子最大的10%的股票
result['code']=result.index

print('================选股结果=====================')
result.to_excel('换手率选股.xlsx')
result.head(10) #显示前10只