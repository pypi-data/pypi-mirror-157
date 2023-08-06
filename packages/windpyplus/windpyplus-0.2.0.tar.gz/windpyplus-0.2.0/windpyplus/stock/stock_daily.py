import re
import pandas as pd

from WindPy import *
w.start()


def stock_daily_adj_one(trade_date=None):
    """_summary_
    stock daily , bfq , adjfactor;
    trade date -- all stock price 
    trade_date like : 2022-07-01
    Args:
        trade_date (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
        dataframe  to sql 
    """
    stocks = w.wset("sectorconstituent",f"date={trade_date};sectorid=a001010100000000").Data[1]
    #print(stocks[-5:])
    data = w.wss(stocks,
                            "pre_close,open,high,low,close,volume,amt,pct_chg,vwap,adjfactor",
                            
                            #   turn,close2,free_turn_n,lastradeday_s,firstradeday_s,rel_ipo_chg,last_trade_day, \
                            #   val_mv_ARD,val_mvc,trade_status,maxupordown,maxup,maxdown,susp_days",
                                     f"tradeDate={trade_date};priceAdj=U;cycle=D;adjDate={trade_date};unit=1"
                                     #usedf=True
                                     )
    #print(data)
    df = pd.DataFrame(data=data.Data, columns=data.Codes, index=data.Fields).T
    df['TRADE_DATE'] = trade_date
    df.reset_index(inplace=True)
    df.rename(columns={"index":"WIND_CODE"},inplace=True)
    print(df)
    return df


def save_stock_day_to_sqlite(): #TODO
    pass


if __name__ == "__main__":
    stock_daily_adj_one('2015-06-03')
    
    


