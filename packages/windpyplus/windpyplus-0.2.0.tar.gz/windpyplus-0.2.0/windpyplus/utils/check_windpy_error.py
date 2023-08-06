import json
from datetime import datetime

from WindPy import w

def check_api_error(func):
    """
    A decorator for WindPy functions, so that if a function fails to retrieve data, it will print the error code and the relevant message before exiting
    :param func: WindPy function that returns a WindData object
    :return: wrapper
    """

    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        if data.ErrorCode != 0:
            print(data)
            exit()
        return data
    return wrapper

# Decorate w.start
w.start = check_api_error(w.start)
print(w.start)
# Decorate w.wset
w.wset = check_api_error(w.wset)
print(w.wset)

# Start WindPy connection
w.start()

# Get the date of today and convert it to a string with format YYYYMMDD
today = datetime.strftime(datetime.today(), "%Y%m%d")
print(today)
# Retrieve the wind codes of the constituent
stock_codes = w.wset("sectorconstituent", "date=" + today + ";windcode=000300.SH;field=wind_code")
print(stock_codes)

# Save the data in json
with open('HS300Constituent.json', mode='w') as f:
    json.dump(stock_codes.Data[0], f)


    
    