from WindPy import *
from datetime import *
import pandas as pd

from windpyplus.utils.dfToExcel import dfToExcel

w.start()


# 定义API报错函数
def verifyResult(errCode):
    assert errCode == 0, "API数据提取错误，ErrorCode={}，具体含义请至帮助文档附件《常见API错误码》中查询。".format(errCode)

def select_stock_by_volume():
    """ """
    # 基于成交量进行选股
    date1 = w.tdaysoffset(-1,datetime.today() , "")
    verifyResult(date1.ErrorCode)
    end_Date = date1.Times[0].strftime("%Y%m%d")

    date2 = w.tdaysoffset(-5, end_Date, "")
    verifyResult(date2.ErrorCode)
    start_Date = date2.Times[0].strftime("%Y%m%d")

    code_list = w.wset("sectorconstituent","date=" + end_Date + ";sectorid=a001010100000000")
    verifyResult(code_list.ErrorCode)   

    volume_average = w.wss(code_list.Data[1],"avg_vol_per","startDate=" + start_Date + ";endDate=" + end_Date + "")
    verifyResult(volume_average.ErrorCode)

    volume = w.wss(code_list.Data[1],"volume","tradeDate=" + end_Date + ";cycle=D")
    verifyResult(volume.ErrorCode)
        
    result = pd.DataFrame(columns = ['股票代码','股票简称','上一个交易日的成交量'])
    for i in range(len(code_list.Data[0])):
        if(volume.Data[0][i]> 3*volume_average.Data[0][i]):
            result.loc[len(result)] = [code_list.Data[1][i], code_list.Data[2][i], volume.Data[0][i]]
            i = i+1
    dfToExcel(result,'vol_select.xlsx') #保存选股结果到excel
    #print(f"保存选股结果到excel: vol_select.xlsx")
    return result

if __name__ == "__main__":
    select_stock_by_volume()