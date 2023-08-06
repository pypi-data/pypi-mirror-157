import pandas as pd 

from windpyplus.utils.tradedate import tradedate
from windpyplus.utils.dfToExcel import dfToExcel
from swl_contains import swl_class

from WindPy import *
w.start()


def swl_daily_oneCode(index_code=None, period=365):
    """
    swl_daily & valucation;
    one index code --periods( all  year days, not trade dates)
    
    Args:
        index_code (_type_, optional): _description_. Defaults to None.
        period (int, optional): _description_. Defaults to 255.

    Returns:
        _type_: _description_
    """
    
    lasttradedate = tradedate(0)[-1]
    data = w.wsd(f"{index_code}", "pre_close,open,high,low,close,volume,amt,pct_chg,vwap,adjfactor, \
    pe_ttm,val_pe_median,pcf_ocf_ttm,  pe_est,estpe_FY1,estpe_FY2,estpe_FY3", 
    f"ED-{period}D", f"{lasttradedate}", "unit=1;rptYear=2021;year=2022")
    #print(data)
    df = pd.DataFrame(data=data.Data, index=data.Fields, columns=data.Times).T
    df["WIND_CODE"] = data.Codes[0]
    df.reset_index(inplace=True)
    df.rename(columns={"index":"TRADE_DATE"},inplace=True)
    print(df)
    return df
    

def swl_daily_one_day(trade_date=None,level="L1"):
    """
    "pre_close,open,high,low,close,volume,amt,pct_chg,vwap,adjfactor,turn,free_turn_n,dq_amtturnover,
    val_mv_ARD,val_mvc,pe_ttm,val_pe_nonnegative,val_pe_median,val_pe_deducted_ttm,pe_lyr,pb_mrq,pb_lyr,ps_ttm,
    pcf_ocf_ttm,val_pcf_ocfttmwgt,dividendyield,dividendyield2,val_pettm_high,val_pettm_low,val_pettm_avg,
    val_pb_high,val_pb_low,val_pb_avg,val_psttm_high,val_psttm_low,val_psttm_avg,val_pslyr_high,val_pslyr_low,
    val_pslyr_avg,val_per,val_pep2,val_pe_percentile,val_pb_percentile,val_dividend_percentile,val_ps_percentile,
    val_pcf_percentile","tradeDate=20220701;priceAdj=U;cycle=D;unit=1;rptYear=2021;startDate=20220602;endDate=20220702")

    Args:
        trdae_date (_type_, optional): _description_. Defaults to None.
        level (str, optional): _description_. Defaults to "L1".
    """
    index_codes = swl_class(level).wind_code.to_list()
    #print(index_codes)
    error_code, df = w.wss(index_codes,
    "pre_close,open,high,low,close,volume,amt,pct_chg,vwap,adjfactor,turn,free_turn_n, pe_ttm,val_pe_nonnegative,val_pe_median,ps_ttm, pcf_ocf_ttm, \
    dividendyield2,val_pettm_high,val_pettm_low,val_pettm_avg,val_pb_avg,val_psttm_avg,val_pslyr_avg,val_pe_percentile,val_pb_percentile,val_dividend_percentile, \
        val_ps_percentile, val_pcf_percentile",
    f"tradeDate={trade_date};priceAdj=U;cycle=D;unit=1;rptYear=2021;startDate=20220602;endDate=20220702",
                 usedf=True)
    df.reset_index(inplace=True)
    df.rename(columns={"index":"WIND_CODE"},inplace=True)
    df["TRADE_DATE"] = trade_date
    df["LEVEL"] = level
    print(df)
    dfToExcel(df, f"swl_day_{level}.xlsx")
    return df
    
if __name__ == "__main__":
    #swl_daily_oneCode("801980.SI")
    #swl_daily_oneCode("859811.SI")
    #swl_daily_one_day("2022-07-01",'L1')
    #swl_daily_one_day("2022-07-01",'L2')
    swl_daily_one_day("2022-07-01","L3")
    
    
  
    