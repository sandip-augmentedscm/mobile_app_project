import numpy as np
import pandas as pd
from numpy import nan
from statistics import mean, stdev
from datetime import datetime, timedelta
from dateutil.relativedelta import *

import warnings
warnings.simplefilter(action='ignore')

from table_territory_master import create_territory_master
from table_customer_master import create_customer_master


def weighted_mean_rem_outlier(a_list, weights, remove = True):
    q3, q1 = np.percentile(a_list, [75 ,25])
    iqr = q3 - q1
    upper_limit = q3 + 1.5*iqr
    lower_limit = q1 - 1.5*iqr
    if remove:
        output = [x if (x >= lower_limit) and (x <= upper_limit)\
                  else nan for x in a_list]
    else:
        output = [x for x in a_list]   
    final_list = [x*w for x,w in zip(output, weights) if not np.isnan(x)]
    return round(sum(final_list)/len(final_list), 2)

def DatetoPeriod(date):
    year = date.year
    month = date.month
    if month <= 9:
        return int(str(year)+'0'+str(month))
    else:
        return int(str(year)+str(month))

def DaysinPeriod(period):
    month_num = int(str(period)[-2:])
    return {
        1 : 31,
        2 : 28, 
        3 : 31,
        4 : 30,
        5 : 31,
        6 : 30,
        7 : 31,
        8 : 31,
        9 : 30,
        10 : 31,
        11 : 30,
        12 : 31
    }[month_num]

def DatetoSubperiod(date):
    if date.day <= 7:
        return 'subperiod_1'
    elif date.day <= 15:
        return 'subperiod_2'
    elif date.day <= 22:
        return 'subperiod_3'
    else:
        return 'subperiod_4'

def calculate_overall_skew(input_df):
    
    input_df.sort_values(by='Bill Date',inplace=True)
    
    # Filter the data for last four months
    current_date = input_df['Bill Date'].max()
    start_date = current_date - pd.offsets.MonthBegin()
    start_date = start_date - relativedelta(months=4)
    input_df = input_df[input_df['Bill Date'] >= start_date]
    input_df = input_df[input_df['Bill Date'] <= current_date]
    
   
    subperiod_list = ['subperiod_1', 'subperiod_2', 'subperiod_3', 'subperiod_4']
    
    input_df['period'] = input_df['Bill Date'].apply(lambda x: DatetoPeriod(x))
    # current_period = input_df.loc[(input_df['Bill Date'] == pd.Timestamp('2018-02-15')), 'period'].values[0]
    
    input_df['subperiod'] = input_df['Bill Date'].apply(lambda x: DatetoSubperiod(x))
    # current_subperiod = input_df.loc[(input_df['Bill Date'] == pd.Timestamp('2018-02-15')), 'subperiod'].values
    
    period_list = input_df['period'].drop_duplicates(keep = 'first').tolist()

    test_df = input_df[['Month Name', 'period', 'subperiod', 'Quantity in KG/LTR',\
                        'Amount To Customer']]
    test_df = test_df.groupby(['Month Name', 'period', 'subperiod'],\
                            as_index=False)['Quantity in KG/LTR', 'Amount To Customer'].sum()

    subperiod_sale_val, subperiod_sale_volm = {}, {}
    for period in period_list[:-1]:
        test_df1 = test_df[test_df['period'] == period]
        test_df1 = test_df1.groupby(['Month Name', 'period'],\
                            as_index=False)['Quantity in KG/LTR', 'Amount To Customer'].sum()
        temp_val, temp_volm = [], []
        for sub_period in subperiod_list:
            test_df2 = test_df[(test_df['subperiod'] == sub_period) & (test_df['period'] == period)]
            
            if len(test_df2)!= 0:
                temp_val.append(round(test_df2['Amount To Customer'].values[0], 2))
                temp_volm.append(round(test_df2['Quantity in KG/LTR'].values[0], 2))
            else:
                temp_val.append(0)
                temp_volm.append(0)
            
        subperiod_sale_val[period] = temp_val
        subperiod_sale_volm[period] = temp_volm

    overall_subperiod_sale_val_df = pd.DataFrame(subperiod_sale_val, index=subperiod_list).T
    overall_subperiod_sale_volm_df = pd.DataFrame(subperiod_sale_volm, index=subperiod_list).T
    
    weights = [0.125, 0.125, 0.25, 0.5]
    avg_overall_val, avg_overall_volm = [], []
    for sub_period in subperiod_list:
        avg_overall_val.append(np.average(overall_subperiod_sale_val_df[sub_period].values, weights=weights))
        avg_overall_volm.append(np.average(overall_subperiod_sale_volm_df[sub_period].values, weights=weights))
    
    return {
        'val' : [round(100*x/sum(avg_overall_val),2) for x in avg_overall_val],
        'volm' : [round(100*x/sum(avg_overall_volm),2) for x in avg_overall_volm]
    }
    
    
def calculate_territory_wise_skew(input_df, territory_df):

    input_df.sort_values(by='Bill Date',inplace=True)
    
    # Filter the data for last four months
    current_date = input_df['Bill Date'].max()
    start_date = current_date - pd.offsets.MonthBegin()
    start_date = start_date - relativedelta(months=4)
    input_df = input_df[input_df['Bill Date'] >= start_date]
    input_df = input_df[input_df['Bill Date'] <= current_date]
    
   
    subperiod_list = ['subperiod_1', 'subperiod_2', 'subperiod_3', 'subperiod_4']
    
    input_df['period'] = input_df['Bill Date'].apply(lambda x: DatetoPeriod(x))
    current_period = input_df.loc[(input_df['Bill Date'] == pd.Timestamp('2018-02-15')), 'period'].values[0]
    
    input_df['subperiod'] = input_df['Bill Date'].apply(lambda x: DatetoSubperiod(x))
    # current_subperiod = input_df.loc[(input_df['Bill Date'] == pd.Timestamp('2018-02-15')), 'subperiod'].values
    
    period_list = input_df['period'].drop_duplicates(keep = 'first').tolist()

    territory_details_df1 = input_df[['Territory Sales Manger','Month Name', 'period', 'subperiod',\
                                'Quantity in KG/LTR', 'Amount To Customer']]
    territory_details_df1['Territory Sales Manger'] = territory_details_df1['Territory Sales Manger'].str.upper()

    test_df = territory_details_df1.groupby(['Territory Sales Manger','Month Name','period', \
                                            'subperiod'],as_index=False)\
    ['Quantity in KG/LTR', 'Amount To Customer'].sum()
    test_df.rename(columns={'Territory Sales Manger':'territory'}, inplace=True)
    test_df['territory'] = test_df['territory'].str.upper()

    territory_list = territory_df['territory_name'].drop_duplicates(keep = 'first').tolist()


    territory_sale_val, territory_sale_volm = {}, {}
    current_period_sale_val, current_period_sale_volm = {}, {}
    for territory in territory_list:
        subperiod_sale_val, subperiod_sale_volm = {}, {}
        for period in period_list:
            test_df1 = test_df[(test_df['period'] == period) & (test_df['territory'] == territory)]
            test_df1 = test_df1.groupby(['Month Name', 'period'],\
                                as_index=False)['Quantity in KG/LTR', 'Amount To Customer'].sum()
            temp_val, temp_volm = [], []
            for sub_period in subperiod_list:
                test_df2 = test_df[(test_df['subperiod'] == sub_period)\
                                & (test_df['period'] == period)\
                                & (test_df['territory'] == territory)]

                if len(test_df2)!= 0:
                    temp_val.append(round(test_df2['Amount To Customer'].values[0], 2))                    
                    temp_volm.append(round(test_df2['Quantity in KG/LTR'].values[0], 2))
                else:
                    temp_val.append(0)
                    temp_volm.append(0)

            subperiod_sale_val[period] = temp_val            
            subperiod_sale_volm[period] = temp_volm
        
        current_period_sale_val[territory] = subperiod_sale_val[current_period]
        current_period_sale_volm[territory] = subperiod_sale_volm[current_period]
        
        del subperiod_sale_val[current_period]  
        del subperiod_sale_volm[current_period]
        
        territory_sale_val[territory] = pd.DataFrame(subperiod_sale_val, index=subperiod_list).T
        territory_sale_volm[territory] = pd.DataFrame(subperiod_sale_volm, index=subperiod_list).T
        
    weights=[0.125, 0.125, 0.25, 0.5]
    avg_territory_sale_val, avg_territory_sale_volm = {}, {}
    for territory in territory_list:
        temp_val, temp_volm = [], []
        for sub_period in subperiod_list:
            temp_val.append(weighted_mean_rem_outlier(territory_sale_val[territory][sub_period].values,\
                                                      weights, remove=True))
            temp_volm.append(weighted_mean_rem_outlier(territory_sale_volm[territory][sub_period].values,\
                                                       weights, remove=True))
        
        avg_territory_sale_val[territory] = [round(100*x/sum(temp_val),2) for x in temp_val]
        avg_territory_sale_volm[territory] = [round(100*x/sum(temp_volm),2) for x in temp_volm]
    
    return {
        'val' : avg_territory_sale_val,
        'volm' : avg_territory_sale_volm,
        'current_val' : current_period_sale_val,
        'current_volm' : current_period_sale_volm
    }


def calculate_customer_wise_skew(input_df, customer_df):
    input_df.sort_values(by='Bill Date',inplace=True)
    
    # Filter the data for last four months
    current_date = input_df['Bill Date'].max()
    start_date = current_date - pd.offsets.MonthBegin()
    start_date = start_date - relativedelta(months=4)
    input_df = input_df[input_df['Bill Date'] >= start_date]
    input_df = input_df[input_df['Bill Date'] <= current_date]
    
   
    subperiod_list = ['subperiod_1', 'subperiod_2', 'subperiod_3', 'subperiod_4']
    
    input_df['period'] = input_df['Bill Date'].apply(lambda x: DatetoPeriod(x))
    current_period = input_df.loc[(input_df['Bill Date'] == pd.Timestamp('2018-02-15')), 'period'].values[0]
    
    input_df['subperiod'] = input_df['Bill Date'].apply(lambda x: DatetoSubperiod(x))
    # current_subperiod = input_df.loc[(input_df['Bill Date'] == pd.Timestamp('2018-02-15')), 'subperiod'].values
    
    period_list = input_df['period'].drop_duplicates(keep = 'first').tolist()
    
    customer_details_df1 = input_df[['Customer Name','Month Name', 'period', 'subperiod',\
                                'Quantity in KG/LTR', 'Amount To Customer']]
    customer_details_df1['Customer Name'] = customer_details_df1['Customer Name'].str.upper()

    test_df = customer_details_df1.groupby(['Customer Name','Month Name','period', 'subperiod'],as_index=False)\
    ['Quantity in KG/LTR', 'Amount To Customer'].sum()

    test_df.rename(columns={'Customer Name':'customer_name'}, inplace=True)
    customer_list = customer_df['customer_name'].drop_duplicates(keep = 'first').tolist()

    customer_sale_val, customer_sale_volm = {}, {}
    current_period_sale_val, current_period_sale_volm = {}, {}
    for customer in customer_list:
        subperiod_sale_val, subperiod_sale_volm = {}, {}
        for period in period_list:
            test_df1 = test_df[(test_df['period'] == period) & (test_df['customer_name'] == customer)]
            test_df1 = test_df1.groupby(['Month Name', 'period'],\
                                as_index=False)['Quantity in KG/LTR', 'Amount To Customer'].sum()
            temp_val, temp_volm = [], []
            for sub_period in subperiod_list:
                test_df2 = test_df[(test_df['subperiod'] == sub_period)\
                                & (test_df['period'] == period)\
                                & (test_df['customer_name'] == customer)]

                if len(test_df2)!= 0:
                    temp_val.append(round(test_df2['Amount To Customer'].values[0], 2))                    
                    temp_volm.append(round(test_df2['Quantity in KG/LTR'].values[0], 2))
                else:
                    temp_val.append(0)
                    temp_volm.append(0)

            subperiod_sale_val[period] = temp_val            
            subperiod_sale_volm[period] = temp_volm
        
        current_period_sale_val[customer] = subperiod_sale_val[current_period]
        current_period_sale_volm[customer] = subperiod_sale_volm[current_period]
        
        del subperiod_sale_val[current_period]  
        del subperiod_sale_volm[current_period]
        
        customer_sale_val[customer] = pd.DataFrame(subperiod_sale_val, index=subperiod_list).T
        customer_sale_volm[customer] = pd.DataFrame(subperiod_sale_volm, index=subperiod_list).T
        
    weights=[0.125, 0.125, 0.25, 0.5]
    avg_customer_sale_val, avg_customer_sale_volm = {}, {}
    for customer in customer_list:
        temp_val, temp_volm = [], []
        for sub_period in subperiod_list:
            temp_val.append(weighted_mean_rem_outlier(customer_sale_val[customer][sub_period].values,\
                                                      weights, remove = True))
            temp_volm.append(weighted_mean_rem_outlier(customer_sale_volm[customer][sub_period].values,\
                                                       weights, remove = True))
        
        avg_customer_sale_val[customer] = [round(100*x/sum(temp_val),2) for x in temp_val]
        avg_customer_sale_volm[customer] = [round(100*x/sum(temp_volm),2) for x in temp_volm]
    
    return {
        'val' : avg_customer_sale_val,
        'volm' : avg_customer_sale_volm,
        'current_val' : current_period_sale_val,
        'current_volm' : current_period_sale_volm
    }
  
if __name__ == '__main__':
    input_df = pd.read_excel('csv_files\\Bellary SD Sales.xlsx')

    # Date today
    current_date = pd.Timestamp('2018-02-15')

    # Filter the data from AUG 1, 2017 to current_date
    input_df = input_df[input_df['Bill Date'] >= pd.Timestamp('2017-08-01')]
    input_df = input_df[input_df['Bill Date'] <= current_date]
        
    territory_master_df = create_territory_master(input_df)
    customer_master_df = create_customer_master(input_df, territory_master_df)
    
    overall_skew_dict = calculate_overall_skew(input_df)
    print(overall_skew_dict)
    
    territory_wise_skew_dict = calculate_territory_wise_skew(input_df, territory_master_df)
    print(territory_wise_skew_dict)
    
    customer_wise_skew_dict = calculate_customer_wise_skew(input_df, customer_master_df)
    print(customer_wise_skew_dict)
