from WindPy import *
w.start()

def all_a_stocks(trade_date=None):
    """w.wset("sectorconstituent","date="+end_Date+";sectorid=a001010100000000")
    """
    if not trade_date:
        date =  w.tdaysoffset(0,datetime.today() , "")
        end_Date =  date.Times[0].strftime("%Y%m%d")  #设置时间为上一个交易日，并转化时间格式
        print(end_Date)
        trade_date = end_Date
        
    codes = w.wset("sectorconstituent",f"date={trade_date};sectorid=a001010100000000")
    code_list = codes.Data[1]   #所有A股 为股票池
    print(code_list[:5])
    print(len(code_list))
    return code_list

if __name__ == "__main__":
    all_a_stocks()
