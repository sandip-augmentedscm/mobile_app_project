import pandas as pd
from calculate_skewness import *

def skewed_actual_runrate(total_sale, skew_percent, current_period, current_date):
    x, y, z, t = skew_percent[0], skew_percent[1], skew_percent[2], skew_percent[3]
    current_subperiod = DatetoSubperiod(current_date)
    
    # Days elapsed in current period
    d1 = current_date.day
    
    # Days in current period
    d = DaysinPeriod(current_period)
    
    # Days in last sub-period
    td = d - 22
    
    # Expected % of sales by today
    if current_subperiod == 'subperiod_1':
        w = x*d1/7
    elif current_subperiod == 'subperiod_2':
        w = x + y*(d1 - 7)/8
    elif current_subperiod == 'subperiod_3':
        w = x + y + z*(d1 - 15)/7
    else:
        w = x + y + z + t*(d1 - 22)/td
    
    # Expected sale at the end of the period
    expected_sale = 100*total_sale/w
    
    # Skewed run rate
    skewed_runrate = round((1/d)*expected_sale, 2)
    
    return skewed_runrate
    

# if __name__ == '__main__':
#     total_sale = 100
#     skew_percent = [10, 15, 25, 60]
#     current_period = 201801
#     current_date = pd.Timestamp('2018-01-18')
    
#     # print(skewed_actual_runrate(total_sale, skew_percent, current_period, current_date))
#     print(skewed_actual_runrate(137875.34, [0.0, 0.0, 51.1, 48.9], 201802, pd.Timestamp('2018-02-15 00:00:00')))
    