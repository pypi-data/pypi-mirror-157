import pandas as pd

from swl_contains import swl_class
from WindPy import *
w.start()

swl_l1 = swl_class("L1")
swl_l1

error_coe, data = w.wss("801010.SI,801030.SI,801040.SI,801050.SI,801080.SI,801110.SI,801120.SI,801130.SI,801140.SI,801150.SI,801160.SI,801170.SI,801180.SI,801200.SI,801210.SI,801230.SI,801710.SI,801720.SI,801730.SI,801740.SI,801750.SI,801760.SI,801770.SI,801780.SI,801790.SI,801880.SI,801890.SI,801950.SI,801960.SI,801970.SI,801980.SI", 
             "val_pb_wgt,val_pe_avg,tech_uppct,tech_downpct,tech_limitdownpct",
             "tradeDate=20220701",
             usedf=True)

print(data)