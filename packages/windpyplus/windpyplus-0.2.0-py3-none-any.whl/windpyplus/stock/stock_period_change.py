from windpyplus.stockSector.allAStock import all_a_stocks
from windpyplus.utils.dfToExcel import dfToExcel
from WindPy import *
w.start()


stocks = all_a_stocks()

def stock_period_change_other(start_date=None, end_date=None):
    """ """
    error_code, data = w.wss(stocks[:5],
    "sec_name,pre_close_per,open_per,high_per,low_per,close_per,max_close_per,min_close_per,chg_per,pct_chg_per,pct_chg_per2,pct_chg_low_per,pct_chg_high_per,pct_chg_lowest_per,pct_chg_highest_per,avg_swing_per,swing_per,vwap_per,pq_avgprice2,turn_per,turn_free_per,pq_avgturn2,avg_turn_per,avg_turn_free_per,vol_per,amt_per,avg_vol_per,avg_amt_per,avg_MV_per,pq_avgmv_nonrestricted,trade_days_per,limitupdays_per,limitdowndays_per,pq_updays_per,pq_downdays_per,high_date_per,low_date_per,max_close_date_per,min_close_date_per,pct_chg_5d,pct_chg_10d,pct_chg_1m,pct_chg_3m,pct_chg_6m,pct_chg_1y,pq_relpctchange",
    "startDate=20220602;endDate=20220702;priceAdj=U;unit=1;currencyType=;index=1",
    usedf=True)
    print(data)
    dfToExcel(data,f"stock_periods_change.xlsx")
    return data


def stock_rt_oh_ol_swl(trade_date=None):
    
    """_summary_
    "pre_close_per,high_per,low_per,close_per,max_close_per,min_close_per,pct_chg_per,pct_chg_per2,
    pct_chg_low_per,pct_chg_high_per,pct_chg_lowest_per,pct_chg_highest_per,trade_days_per,limitupdays_per,
    limitdowndays_per,pq_updays_per,pq_downdays_per,pct_chg_5d,pct_chg_10d,pct_chg_1m,pct_chg_3m,pct_chg_6m,
    pct_chg_1y,sec_name,ipo_date,mkt,industry_sw_2021","startDate=20220602;endDate=20220702;priceAdj=U;
    tradeDate=20220701;industryType=4")
    
        trade_date (_type_, optional): _description_. Defaults to None.
    """
    error_code, data = w.wss(stocks,
                             "pre_close_per,high_per,low_per,close_per,max_close_per,min_close_per,pct_chg_per,pct_chg_per2, \
    pct_chg_low_per,pct_chg_high_per,pct_chg_lowest_per,pct_chg_highest_per,trade_days_per,limitupdays_per, \
    limitdowndays_per,pq_updays_per,pq_downdays_per,pct_chg_5d,pct_chg_10d,pct_chg_1m,pct_chg_3m,pct_chg_6m, \
    pct_chg_1y,sec_name,ipo_date,mkt,industry_sw_2021","startDate=20220602;endDate=20220702;priceAdj=U; \
    tradeDate=20220701;industryType=4",
    usedf=True
    )
    print(data)
    dfToExcel(data, f"stock_rt_oh_ol.xlsx")
    return data

if __name__ ==  "__main__":
    stock_period_change_other(start_date=None, end_date=None)
    #stock_rt_oh_ol_swl(trade_date=None)

