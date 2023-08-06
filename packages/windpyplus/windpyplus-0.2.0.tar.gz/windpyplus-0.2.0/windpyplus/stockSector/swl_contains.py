import pandas as pd

from WindPy import *
w.start()


def swl_class(level= "L3"):
    """_summary_
    L1: w.wset("sectorconstituent","date=2022-07-02;sectorid=a39901011g000000")
    L2: w.wset("sectorconstituent","date=2022-07-02;sectorid=a39901011h000000")
    L3: w.wset("sectorconstituent","date=2022-07-02;sectorid=a39901011i000000")
    Args:
        level (str, optional): _description_. Defaults to "L1".
    """
    if level == "L1":
        sid = "a39901011g000000"
    if level == "L2":
        sid = "a39901011h000000"
    if level == "L3":
        sid = "a39901011i000000"
    # 获取申万1,2,3级行业的成分股
    errorCode,sw_index=w.wset("sectorconstituent",f"date=2022-07-02;sectorid={sid}",usedf=True)
    print(sw_index)
    sw_index["level"] = level
    return sw_index

def swl_level_all():
    swl = pd.DataFrame()
    for l in ["L1","L2","L3"]:
        swl = swl.append(swl_class(l))
    print(swl)
    return swl

    
if __name__ == "__main__":
    from windpyplus.utils.dfToExcel import dfToExcel
    #df = swl_class(level="L3")
    df = swl_level_all()
    dfToExcel(df, "swl_all.xlsx")
    
    
    
    
    
    
    